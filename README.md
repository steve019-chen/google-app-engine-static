# Website Hosted in Google Cloud

Repository to host a template driven static website in Google Cloud with web page content maintained as in separate html files locally.

## Steps to Implement
1. Create a project in Google Cloud Console: https://console.cloud.google.com
2. Clone this repository to your HD.
3. Adjust html/base.html and html/home.html for your website.
4. Deploy the updated site to Google cloud (sudo gcloud app deploy --project projectid --no-promote)
5. Review your new website with the version url provided.

You may want to bind your new Google Cloud project with a proper domain name. How this is done is well described in the Google Cloud documentation.

## Steps to Add a Page
1. Create a new template in the folder html
2. Bind the new template with a website request path in pages.py
3. Deploy the modified application to Google Cloud

## Background
https://www.simaec.net/website-development/google-app-engine-hosting/
