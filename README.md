# colorbyautomation

Take a input json file and creates views in Revit based on the JSON settings.
```json
{
    "ViewCombinations": [
      {
        "ViewCombinationName": "Slab vs Duct",
        "CategoriesAndColor": [
          {
            "Category": "Slabs",
            "Color": "#FF0000",  // Red
            "Transparency": "50%"
          },
          {
            "Category": "Ducts",
            "Color": "#00FF00",  // Green
            "Transparency": "50%"
          }
        ],
        "FanByTypeName": "Y",
        "FanByProperties": {
          "Rating": "Y",
          "Comment": "Rating, Comment"
        },
        "FanByLink": "Y",
        "ViewRange": {
          "TopOffsetRelativeToLevel": "6",
          "BottomOffsetRelativeToLevel": "0",
          "CutPlaneOffsetRelativeToLevel": "4",
          "ViewDepthOffsetRelativeToLevel": "12"
        },
        "HostLevelsToProcess": [
          "Level 1","Level 3" ]
      },
      {
        "ViewCombinationName": "Rated Walls vs Beams",
        "CategoriesAndColor": [
          {
            "Category": "Walls",
            "Color": "#FF0000",  // Red
            "Transparency": "40%"
          },
          {
            "Category": "Beams",
            "Color": "#00FF00",  // Green
            "Transparency": "40%"
          }
        ],
        "FanByTypeName": "N",
        "FanByProperties": {
          "Rating": "N",
          "Comment": ""
        },
        "FanByLink": "N",
        "ViewRange": {
          "TopOffsetRelativeToLevel": "0",
          "BottomOffsetRelativeToLevel": "96",
          "CutPlaneOffsetRelativeToLevel": "48",
          "ViewDepthOffsetRelativeToLevel": "0"
        },
        "HostLevelsToProcess": "all"
      }
    ]
  }
  ```
