# AWS Slack Alerts

Lambda function to send AWS alerts to a Slack channel. This function was originally developed by me while working at
[Morris Technology](http://www.morristechnology.com) ([@morris-tech](https://github.com/morris-tech)). I have recently
restructured it so that it can be expanded to support more event types.

## Event Support

This function was originally developed to serve auto scaling notifications, CloudWatch alarms, and AWS Health Events
into Slack, but it should support (for the most part) other SNS events and CloudWatch Events.

## Deployment
You can easily deploy this function to your account using [Serverless](https://serverless.com/)
(refer to their website for information on how to install Serverless):

### Get API token
In order to communicate with Slack, you need to setup an API token. This is easiest done by creating a Slack app on
your Slack team until I am able to distribute an app publicly.

### Deploy function

```
sls deploy --token=<Your Slack Token> --channel='#channel'
```
