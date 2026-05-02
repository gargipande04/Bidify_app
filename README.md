This code is dedicated to the public domain to the maximum extent permitted by applicable law, pursuant to  
[CC0](http://creativecommons.org/publicdomain/zero/1.0/).

# cw3-webprogramming
URL of deployed application: https://django-psql-persistent-web-apps-ec22777.apps.a.comp-teach.qmul.ac.uk
## Admin
**Username:**  
admin
**Email:** 
admin@gmail.com
**Password:**
admin@password

## Test Users

- Username: test1  
  Password: password123

- Username: test2
  Password: password123

- Username: test4 
  Password: password123

- Username: test6 
  Password: password123

- Username: test7  
  Password: password123

- Username: test8  
  Password: password123

Assigned:

Mohammed Ali Bin Shamlan: 
Users of the site should be able to bid for an item, before the end date/time of that item.
The site must contain a page listing all the items that are currently available, with the ability to “search” for items based on a given keyword. For instance, searching for “table” should return the list of items that have “table” as part of their title or description. The searching mechanism should be done using Ajax (so no page refreshes).

Saif Khadraoui:
Users can create an account (signup) on the web app and login/logout. You should use a custom User model (as explained here) which inherits from Django's AbstractUser model. Make use of Django's authentication framework. The signup and login can be done using Django forms and templates. Vue only needs to be used once the user is authenticated.
Your custom user model should then also have a profile image, email, and date of birth of the user. The user should be able to edit all these fields in a "profile page". Changes to the profile page should be saved via Ajax (using Vue and the fetch API).
Include a page where users can post a new item for auction. Items should contain a title, a description, starting price, a picture and the date/time the auction finishes. Each item should also have its own page.

Gargi Pande: 
Users are able to send questions to the item owner about the condition of the item, and the owner is able to reply to those questions. These questions and answers should be visible to all users of the site.
At the end of the auction, the winner receives an email confirming that they should proceed to purchase the item. This feature should be implemented using cron jobs and Django's send_mail function. You should create a temporary Gmail account for your group and use that to send emails.


Contribution to deliverable:
Saif Khadraoui: Created UI for landing page, login page, signup page and list item page. Created django views and models necessary for those pages including logging out, bidding function

Mohammed Ali Bin Shamlan: 
I updated the Items page with a few UX improvements: added client-side sorting (ending soon / price / title), filters for min & max price and “has image”, plus category browsing/selection and a clear category option. I also added pagination with a “Load more” button, skeleton loading while items are fetching, and a results summary (“Showing X of Y”). I added a reset/“Clear all” control (styled to match the filter boxes) and debounced search so it auto-searches while typing (still works with the Search button too)

Gargi Pande: 
profile page, cron job, deployement, question to owner function, wishlist, categories, saving listings and bids, home page recommendations

