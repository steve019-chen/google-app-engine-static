# Website Hosted in Google Cloud

Repository to setup a website with static web pages hosted in Google Cloud. Content of each page of the website is maintained with a dedicated template. All templates share a common base template.

## Steps to Implement
1. Create a project in Google Cloud Console: https://console.cloud.google.com
2. Pull a clone of this repository: https://github.com/KHMuller/google-app-engine-static
3. Modify html/base.html and html/home.html for your website.
4. Deploy the updated site to Google cloud (sudo gcloud app deploy --project projectid --no-promote)
5. Test your new website with the provided version url

You may want to bind your new Google Cloud project with a proper domain name. How this is done is well described in the Google Cloud documentation.

## Steps to Add a Page
1. Create a new template in the folder html
2. Bind the new template with a website request path in pages.py
3. Deploy the modified application to Google Cloud

## Background
https://www.simaec.net/website-development/google-app-engine-hosting/
