<#
.SYNOPSIS
    Allows to redeploy supporting tools for a BPMN project by building a Docker image and updating an Azure Container App.

.DESCRIPTION
    This script is designed to perform the deployment of supporting tools for a BPMN project. It serves as a template for implementing functionality that automates the process of building a Docker image and updating an Azure Container App.

    - It assumes only one Azure Container Registry (ACR) is available in the specified resource group and uses the first ACR found for building the Docker image.
    - It checks for a `.bpmn` file in the current directory to determine the project ID.
    - It builds a Docker image using the current folder as the context and tags it with the project ID.
    - It updates the specified Azure Container App with the newly built image.

    NOTES
    - This script is a template and may require modifications to fit specific project requirements or environments.
    - If tools signatures were changed, you'll need to update the AI Foundry Agents OpenAPI specs as well.

.PARAMETER ResourceGroup
    The name of the Azure resource group where the resources are located.

.EXAMPLE
    PS C:\> .\deploy_tools.ps1 -ResourceGroup "MyResourceGroup"
    An example demonstrating how to execute the script with the necessary parameters.
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$ResourceGroup
)

# Get the current folder name
$currentFolder = Get-Location
$bpmnFile = Get-ChildItem -Path $currentFolder -Filter *.bpmn | Select-Object -First 1
if (-not $bpmnFile) {
    Write-Error "No .bpmn file found in the current folder."
    exit 1
}
$projectId = $bpmnFile.BaseName
$containerAppName = "tools-$projectId"
Write-Output "Detected project ID: $projectId"
Write-Output "Target container app: $containerAppName"

# List Azure Container Registries in the resource group
$acrListJson = az acr list --resource-group $ResourceGroup --output json
$acrList = $acrListJson | ConvertFrom-Json

if (-not $acrList -or $acrList.Count -eq 0) {
    Write-Error "No Azure Container Registry found in resource group '$ResourceGroup'."
    exit 1
}

# Use the first ACR found
$acr = $acrList[0]
$loginServer = $acr.loginServer

Write-Output "Using ACR: $acrName (Login Server: $loginServer)"

# Define docker image name and tag based on folder name
$imageName = "tools-$projectId:latest"
Write-Output "Building image: $imageName"

# Build the Docker image in ACR from the current folder
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$buildCommand = "az acr build --registry $acrName --resource-group $ResourceGroup --image $imageName --image tools-$projectId:build-$timestamp ."
Write-Output "Executing: $buildCommand"
Invoke-Expression $buildCommand

# Compose the full image reference
$fullImageName = "$loginServer/$imageName"
Write-Output "Full image reference: $fullImageName"

# Update the Container App with the new image from ACR
$updateCommand = "az containerapp update -n $containerAppName -g $ResourceGroup --image $fullImageName"
Write-Output "Executing: $updateCommand"
Invoke-Expression $updateCommand