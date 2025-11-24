import subprocess
from .embed import embedding_function, query_function
import chromadb
from hashlib import md5
from datetime import datetime
from transformers import AutoTokenizer

# Execute the PowerShell command using subprocess.run()
# The powershell.exe executable is a required part of the command list
# capture_output=True saves the output and errors
# text=True decodes the output as a string
def run_command(command):
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8"
        )
        
        return result
        
    except subprocess.CalledProcessError as e:
        print(f"Error executing PowerShell command: {e.stderr}")

# <https://www.google.com/search?sourceid=chrome&udm=50&aep=42&q=These+cmdlet+can+access+onenote%2C+%24onenote+%3D+New-Object+-ComObject+OneNote.Application%0A%5Bxml%5D%24hierarchy+%3D+%22%22%0A%24onenote.GetHierarchy%28%22%22%2C+%5BMicrosoft.Office.InterOp.OneNote.HierarchyScope%5D%3A%3AhsPages%2C+%5Bref%5D%24hierarchy%29%0A%24hierarchy.Notebooks.Notebook+%7C+Format-Table+Name%2C+Path%2C+isUnread%2C+refer+it+and+tell+me+how+to+access+mail+like+it%3F&mstk=AUtExfDwpEmBMxYp2xZZCgBmasuwwLESD6x7wtXEhT6j4kZughc9lsExBb27kkqPs-6JX3YoN1Wpn2Nc7RJkyIoB8x4HL9kafDNNtpPqXFOqCcPLYhQfHkl1NpqZcBubW-FvsAPMhqIvzvQtTFLKfpswhC5W-qM7Wchrq3o&csuir=1&mtid=8O72aIaMOfKP0PEPsPbEmA4>
# Sort will be very slow, so cannot use this: $inboxItems | Sort-Object -Property ReceivedTime -Descending | Select-Object -First 10 Subject, SenderName, ReceivedTime, UnRead | Format-Table
mail_command = """
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8
$outlook = New-Object -ComObject Outlook.Application
$namespace = $outlook.GetNameSpace("MAPI")
$inbox = $namespace.GetDefaultFolder([Microsoft.Office.Interop.Outlook.OlDefaultFolders]::olFolderSentMail)
$inboxItems = $inbox.Items
$counter = 0
foreach ($item in $inboxItems) {{
    if ($counter -gt {mail_index}) {{break}}
    if ($counter -eq {mail_index}) {{
        Write-Host @"
### Head
Subject: $($item.Subject)
Sender: $($item.SenderName)
Recipients: $(($item.Recipients | ForEach-Object {{ $_.Name }}) -join '; ')
Sent Time: $($item.SentOn)
Received Time: $($item.ReceivedTime)
### Body
$($item.Body)
"@
    }}
    $counter++
}}
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($inboxItems) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($inbox) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($namespace) | Out-Null
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($outlook) | Out-Null
"""

class MailSplitter:
    def __init__(self, model_dir):
        self.model_dir = model_dir
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_dir, 
            padding_side="left", 
            trust_remote_code=True
        )

    def split(self, content, chunk_size, chunk_overlap):
        # Validate input parameters
        if not isinstance(content, str):
            raise TypeError("content must be a string")
        if not isinstance(chunk_size, int) or chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer")
        if not isinstance(chunk_overlap, int) or chunk_overlap < 0:
            raise ValueError("chunk_overlap must be a non-negative integer")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        
        # Tokenize the content
        tokens = self.tokenizer.tokenize(content)
        
        # Handle empty content case
        if not tokens:
            return []
        
        chunks = []
        step = chunk_size - chunk_overlap
        for i in range(0, len(tokens), step):
            chunk_tokens = tokens[i:i + chunk_size]
            chunk_text = self.tokenizer.convert_tokens_to_string(chunk_tokens)
            chunks.append(chunk_text)
        
        return chunks

def push_to_database(database_name, docs, embeds, metas, collection_name="mail_collection"):
    client = chromadb.PersistentClient(database_name)
    try:
        collection = client.get_collection(name=collection_name)
    except:
        collection = client.create_collection(name=collection_name)
    collection.add(
        ids=[md5(d.encode()).hexdigest() for d in docs],
        embeddings=embeds,
        documents=docs,
        metadatas=[metas]*len(docs)
    )

def query_mail(query, k_first, embed_model, database_name, collection_name="mail_collection"):
    client = chromadb.PersistentClient(database_name)
    try:
        collection = client.get_collection(name=collection_name)
    except:
        collection = client.create_collection(name=collection_name)
    return collection.query(query_function(query, embed_model), n_results=k_first)

def index_mail(embed_model, database_name, mail_count=20):
    splitter = MailSplitter(embed_model)
    for i in range(mail_count):
        command = mail_command.format(mail_index=i)
        mail_content = run_command(command).stdout
        try:
            _, subject, body = mail_content.split('### ',2)
        except:
            print(mail_content)
        assert subject.startswith('Head\n')
        assert body.startswith('Body\n')
        docs = splitter.split(body.split('\n', 1)[-1], chunk_size=256, chunk_overlap=64)
        embeds = embedding_function(docs, embed_model)
        metas = dict(l.split(': ', 1) for l in subject.split('\n', 1)[-1].splitlines())
        metas["Sent Time"] = datetime.strptime(metas["Sent Time"], "%m/%d/%Y %H:%M:%S").isoformat()
        metas["Received Time"] = datetime.strptime(metas["Received Time"], "%m/%d/%Y %H:%M:%S").isoformat()
        push_to_database(database_name, docs, embeds, metas)
