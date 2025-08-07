# Future improvements and updates

These are things that are not critical to functionality but that I want to address later.

## Main page

### Species timeline overview
- text is too small especially on smaller screens - i think it scales down when you reduce the browser size / width. Some discussion of this here: https://talk.observablehq.com/t/label-font-size/2273/3
- the timeline jumps from 2018 to 2021 without any indication so it is a bit misleading - can we have some separation or indicator - like maybe a vertical line? Or a label of some kind? - that makes it a bit clearer that it's two different years?
- the color scale goes from white to dark blue, so when we try to show "not data" as white, it just looks like it could be a really low, but valid, number. Maybe use a completely different color like a gray or something. 

### Map
- the info pop-ups show years and a date range, and they don't quite match

## General
- there are way more deployment entries than what we have data for. I want to only use/include deployement metadata for the years for which we have temp/depth/detection data (so should be ~2018 and ~2021 - based on the files in )
- throughout the site we refer to the detections as species. they mostly are species but not all - there are also annotations for different, non-biological sounds like static, chain, waves, rain. So I need to update wording to be more flexible