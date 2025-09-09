Please refer to the following project planning files:

notes/PROJECT-PLAN.md -- this is the big picture plan, which describes in detail how we can build upon previous work. 

notes/MVP-PLAN.md -- this is the minimum viable product plan, which describes in detail what we need to build to get the MVP up and running. We will start with this but it will be good to have an awareness of the main project plan, even if it is not fully implemented yet. 

notes/RAW-DATA-DESCRIPTION.md -- this describes all the raw data that we have access to at this time. All raw data are stored in data/raw/ with specifics on content and format included in this description file. 

# Extra notes for claude code
- don't write code or run anything unless I specifically say to do so. I like to discuss things first.
- use uv for python dependency management
- when constructing marimo notebook files, please rememeber that we can't define variables multiple times in the same file or there will be conflicts due to the reactive nature of this type of notebook. 