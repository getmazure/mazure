using FluentAssertions;

// To interact with Azure
using Azure.Core.Pipeline;
using Azure.Identity;
using Azure.Storage.Blobs;
using Azure.Storage.Blobs.Models;

using System.Net;
using System.Net.Security;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;


public class StorageBlobTest
{
    [Fact]
    public async Task TestStorageFileUpload()
    {

        var handler = new HttpClientHandler();
        handler = new HttpClientHandler
            {
                ClientCertificateOptions = ClientCertificateOption.Manual,
                ServerCertificateCustomValidationCallback =
                    (httpRequestMessage, cert, cetChain, policyErrors) => true
            };
        var blobClientOptions = new BlobClientOptions();
        blobClientOptions.Transport = new HttpClientTransport(handler);

        var blobServiceClient = new BlobServiceClient(
            new Uri("https://storage_account" + Guid.NewGuid().ToString() + ".blob.core.windows.net"),
            //new DefaultAzureCredential(),
            blobClientOptions
        );

        string containerName = "quickstartblobs" + Guid.NewGuid().ToString();

        // Create the container and return a container client object
        BlobContainerClient containerClient = await blobServiceClient.CreateBlobContainerAsync(containerName);

        // Create a local file in the ./data/ directory for uploading and downloading
        string localPath = "data";
        Directory.CreateDirectory(localPath);
        string fileName = "quickstart" + Guid.NewGuid().ToString() + ".txt";
        string localFilePath = Path.Combine(localPath, fileName);

        // Write text to the file
        await File.WriteAllTextAsync(localFilePath, "Hello, World!");

        // Get a reference to a blob
        BlobClient blobClient = containerClient.GetBlobClient(fileName);

        Console.WriteLine("Uploading to Blob storage as blob:\n\t {0}\n", blobClient.Uri);

        // Upload data from the local file
        await blobClient.UploadAsync(localFilePath, true);

        Console.WriteLine("Listing blobs...");

        // List all blobs in the container
        await foreach (BlobItem blobItem in containerClient.GetBlobsAsync())
        {
            Console.WriteLine("\t" + blobItem.Name);
        }

        // Download the blob to a local file
        // Append the string "DOWNLOADED" before the .txt extension
        // so you can compare the files in the data directory
        string downloadFilePath = localFilePath.Replace(".txt", "DOWNLOADED.txt");

        Console.WriteLine("\nDownloading blob to\n\t{0}\n", downloadFilePath);

        // Download the blob's contents and save it to a file
        await blobClient.DownloadToAsync(downloadFilePath);

        Console.WriteLine("Deleting blob container...");
        await containerClient.DeleteAsync();

        Console.WriteLine("Deleting the local source and downloaded files...");
        File.Delete(localFilePath);
        File.Delete(downloadFilePath);

        Console.WriteLine("Done");
    }
}
