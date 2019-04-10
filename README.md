# School-Vacation with HomeAssistant Sensor Custom Component
Get School Vacation in HomeAssistant
 This sensor checks every hour whether it is a day off from school.
It's very useful if you set a input_bolean in HA cause you can make automation that set if is vacation or not..
example :
```python
- id: Set_School_Mode_Off
  alias: Set School Mode Off
  trigger: 
  - platform: state
    entity_id: sensor.school_is_vacation
    to: 'True'
  condition: []
  action:
  - data:
      entity_id: input_boolean.school_auto
    service: input_boolean.turn_off
 ```
 ## Guide How to use it
       
### Requirements
 * First need to create folder "school_holidays" in your HomeAssistant config /custom_components folder
* Copy python file "sensor.py" to the HA config /custom_components/school_holidays/ folder.
* Now you need to add those lines in HA sensor.yaml (if you dispated your configs file)  /  configurtion.yaml :
 ```python
 - platform: school_holidays
   friday: False
   resources:
     - is_vacation
     - summary
  ```
  and if you want to use it with input_boolean here is the example :
  ```python
  input_boolean:
    school_auto:
      name: School Mode
      icon: mdi:school
  ```
  ### Entity Requirment
  
  friday - set True if your kids learn in friday , else set it false 
  
  ### Sensor Views Options :
 * in group.yaml:
 ```python
  school:
  name: "מצב לימודים"
  view: no
  entities:
    - sensor.school_summary
    - input_boolean.school_auto 
 ```
 
 * Or in ui-lovelace.yaml :
 
 ```python
  - type: entities
        title: "בית ספר"
        show_header_toggle: false
        entities:
          - sensor.school_summary
          - input_boolean.school_auto  
 ```
 * All sensors icon already set , but you can always customize them..
 
 # Good Luck !
