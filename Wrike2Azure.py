import requests
import json
import base64

# Example usage
wrike_token = "eyJ0dCI6InAiLCJhbGciOiJIUzI1NiIsInR2IjoiMSJ9.eyJkIjoie1wiYVwiOjE3OTQyMjMsXCJpXCI6OTExNTI4NCxcImNcIjo0Njg2OTQ0LFwidVwiOjE5MDM0OTQ2LFwiclwiOlwiVVNcIixcInNcIjpbXCJXXCIsXCJGXCIsXCJJXCIsXCJVXCIsXCJLXCIsXCJDXCIsXCJEXCIsXCJNXCIsXCJBXCIsXCJMXCIsXCJQXCJdLFwielwiOltdLFwidFwiOjB9IiwiaWF0IjoxNzIwMTczNTI3fQ.ja5GmkzFZ7k5Ect3kYBv1bYfHVuuUMKc515mtdjrKdw"
premalink = "https://www.wrike.com/open.htm?id=1364764314"
folder_id = ""  # Initialize with an empty string
azure_pat = "gr5pjuowtywvde73yk4hbrhcpl4jgdmdusjtaky4iegmacki57zq"
organization = "rapyuta-robotics"
project = "sootballs"



# Function to fetch tasks from Wrike
def fetch_wrike_tasks():
    url = "https://www.wrike.com/api/v4"
    headers = {"Authorization": f"Bearer {wrike_token}"}
    response = requests.get(f'{url}/folders/{folder_id}/tasks?&fields=["authorIds","customItemTypeId","responsibleIds","description","hasAttachments","dependencyIds","superParentIds","superTaskIds","metadata","customFields","parentIds","sharedIds","recurrent","briefDescription","attachmentCount","subTaskIds"]&sortField=CreatedDate', headers=headers)
    
    if response.status_code == 200:
        return response.json()['data']
    else:
        response.raise_for_status()

# Fetch folder ID
def get_folder_id():
    url = "https://www.wrike.com/api/v4"
    headers = {'Authorization': f'bearer {wrike_token}',}
    response = requests.get(f'{url}/folders?permalink={premalink}', headers=headers)
    
    if response.status_code == 200:
        folder_details = response.json()
        return folder_details['data'][0]['id']
    else:
        print(f'Failed to get folder id: {response.status_code}')
        print(response.text)
        return None

# Fetch user details given a user ID.
def get_user_details(user_id):
    url = "https://www.wrike.com/api/v4"
    headers = {'Authorization': f'Bearer {wrike_token}'}
    response = requests.get(f'{url}/users/{user_id}', headers=headers)
    
    defaultAssignee = 'vaseekaran.sl@rapyuta-robotics.com'

    if response.status_code == 200:
        user_name = response.json()['data'][0]
        if user_name:
            return user_name['primaryEmail']
        else:
            print("Assignee is Not Found. Set to Default Assignee.")
            return defaultAssignee
    else:
        print(f'Failed to get user details: {response.status_code}')
        print(response.text)
        return None

# Get Folder Details:
def get_folder_details():
    url = "https://www.wrike.com/api/v4"
    headers = {'Authorization': f'Bearer {wrike_token}'}
    response = requests.get(f'{url}/folders/{folder_id}', headers=headers)
    
    if response.status_code == 200:
        folder_details = response.json()
        return folder_details['data'][0]
    else:
        print(f'Failed to get folder details: {response.status_code}') 
        print(response.text)
        return None

# Function to create tasks in Azure Boards
def create_azure_task(task_data):
    workItemType = "bug"
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/${workItemType}?api-version=6.0"
    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Basic {base64.b64encode(f':{azure_pat}'.encode()).decode()}"
    }
    body = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": task_data['title']
        },
        {
            "op": "add",
            "path": "/fields/System.State",
            "value": task_data['state']
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.TCM.SystemInfo",
            "value": task_data['description']
        },
        {
            "op": "add",
            "path": "/fields/System.CreatedDate",
            "value": task_data['created_date']
        },
        {
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": task_data['assignee']
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Scheduling.StoryPoints",
            "value": task_data['story_point']
        },
        {
            "op": "add",
            "path": "/fields/Custom.PhaseDetection",
            "value": task_data['phase_detected']
        },
        {
            "op": "add",
            "path": "/fields/Custom.DetectedRelease2",
            "value": task_data['detected_release']
        },
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Severity",
            "value": task_data['priority']
        },
        {
            "op": "add",
            "path": "/fields/Custom.AssignedSquad",
            "value": task_data['assigned_squad']
        },
        {
            "op": "add",
            "path": "/fields/Custom.ReportedBy",
            "value": task_data['reported_by']
        },   
        {
            "op": "add",
            "path": "/fields/Microsoft.VSTS.Common.Activity",
            "value": task_data['issue_importance']
        },
        {
            "op": "add",
            "path": "/fields/Custom.Contact",
            "value": task_data['contact']
        },
        {
            "op": "add", 
            "path": "/fields/System.AreaPath", 
            "value": task_data['area_path']
        },
        {
            "op": "add", 
            "path": "/fields/System.IterationPath", 
            "value": task_data['iteration_path']
        },
        {
            "op": "add", 
            "path": "/fields/System.CommentCount", 
            "value": task_data['comment_count']
        }
    ]
    response = requests.post(url, headers=headers, data=json.dumps(body))
    
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        response.raise_for_status()


# Function to create tasks in Azure Boards
def create_azure_subtask(task_data):
    workItemType = "bug"
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/${workItemType}?api-version=6.0"
    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Basic {base64.b64encode(f':{azure_pat}'.encode()).decode()}"
    }
    body = [
        {
            "op": "add",
            "path": "/fields/System.Title",
            "value": task_data['title']
        },
        {
            "op": "add",
            "path": "/fields/System.AssignedTo",
            "value": task_data['assignee']
        }
    ]
    response = requests.post(url, headers=headers, data=json.dumps(body))
    
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        response.raise_for_status()

# Function to get subtask details from Wrike
def get_subtask_details(subtask_id):
    url = "https://www.wrike.com/api/v4"
    headers = {'Authorization': f'Bearer {wrike_token}'}
    response = requests.get(f'{url}/tasks/{subtask_id}', headers=headers)
    
    if response.status_code == 200:
        return response.json()['data'][0]
    else:
        print(f'Failed to get subtask details: {response.status_code}')
        print(response.text)
        return None

# Function to create a work item link in Azure Boards
def create_work_item_link(parent_id, child_id):
    url = f"https://dev.azure.com/{organization}/{project}/_apis/wit/workitems/{parent_id}?api-version=6.0"
    headers = {
        "Content-Type": "application/json-patch+json",
        "Authorization": f"Basic {base64.b64encode(f':{azure_pat}'.encode()).decode()}"
    }
    body = [
        {
            "op": "add",
            "path": "/relations/-",
            "value": {
                "rel": "System.LinkTypes.Hierarchy-Forward",
                "url": f"https://dev.azure.com/{organization}/{project}/_apis/wit/workItems/{child_id}",
                "attributes": {
                    "comment": "Linking child task to parent task"
                }
            }
        }
    ]
    response = requests.patch(url, headers=headers, data=json.dumps(body))
    
    if response.status_code == 200 or response.status_code == 201:
        return response.json()
    else:
        if response.status_code == 400 and "WorkItemLinkAddExtraParentException" in response.text:
            print(f"Task {child_id} already has a parent.")
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Response Text: {response.text}")
        response.raise_for_status()

# Function to migrate tasks from Wrike to Azure Boards
def migrate_tasks():
    try:
        wrike_tasks = fetch_wrike_tasks()
        print_tasks(wrike_tasks)  # Print fetched tasks for verification

        for task in wrike_tasks:
            assignee_ids = task.get('responsibleIds', [])
            assignee_name = ""
            for assignee_id in assignee_ids:
                assignee_name = get_user_details(assignee_id)

            #Description
            description = task['description']

            #Area Path
            area_path = "sootballs\\issues"

            #State
            state = "Active"

            #iteration_path
            iteration_path = "sootballs\\PI2"

            #Story Points
            story_point = task['customFields'][9]['value']

            #Phase Detected
            phase_detected = task['customFields'][3]['value']

            #Detected Realease
            detected_realease = task['customFields'][0]['value']
            
            #Assigned Squad
            assigned_squad = task['customFields'][1]['value']

            #Priority:
            priority = task['customFields'][2]['value']

            #Reported By:
            reported_by = task['customFields'][4]['value']

            #Issue importance
            issue_importance = task['customFields'][5]['value']

            #Created Date
            created_date = task['createdDate']

            #Commant Count
            comment_count = task['attachmentCount']

            #Contact
            contact = task['customFields'][8]['value']

            task_data = {
                "title" : task['title'],
                "state" : state, 
                "description": description,
                "assignee": assignee_name,
                "area_path": area_path,
                "iteration_path" : iteration_path,
                "priority" : priority,
                "story_point" : story_point,
                "detected_release" : detected_realease,
                "phase_detected" : phase_detected,
                "assigned_squad" : assigned_squad,
                "reported_by" : reported_by,
                "issue_importance" : issue_importance,
                "created_date" : created_date,
                "comment_count" : comment_count,
                "contact" : contact
            }

            #print(task_data)

            created_task = create_azure_task(task_data)
            print(f"Created Parent task: {created_task['id']} - {created_task['fields']['System.Title']}")

            # Handle subtasks
            for subtask_id in task.get('subTaskIds', []):
                subtask_details = get_subtask_details(subtask_id)
                if subtask_details:
                    subtask_title = subtask_details["title"]

                    #SubTask Assignee:
                    subtask_assignees = [get_user_details(user_id) for user_id in subtask_details.get('responsibleIds', [])]
                    if not subtask_assignees :
                        subtask_assignees = ["vaseekaran.sl@rapyuta-robotics.com"]  # Set to default assignee if no assignees are found
                    
                    print(f"Creating subtask: `{subtask_title}` for parent task: `{task['title']}` with area path: `{area_path}`")
                    azure_subtask = create_azure_subtask({
                        "title": subtask_title,
                        "assignee": subtask_assignees[0]
                    })
                    print(f"Created subtask: `{azure_subtask['id']}` for parent task: `{created_task['id']}` \n")
                    try:
                        create_work_item_link(created_task['id'], azure_subtask['id'])
                    except requests.exceptions.HTTPError:
                        # Handle the case where the subtask already has a parent
                        print(f"Subtask {azure_subtask['id']} could not be linked to {created_task['id']} due to existing parent link.")
    except Exception as e:
        print(f"An error occurred: {e}")



# Function to format task data from Wrike
def format_task(task):
    task_details = (
        f"ID: {task['id']}\n"
        f"Title: {task['title']}\n"
        f"Status: {task['status']}\n"
        f"Importance: {task['importance']}\n"
        f"Created Date: {task['createdDate']}\n"
        f"Updated Date: {task['updatedDate']}\n"
        f"Start Date: {task['dates'].get('start', 'N/A')}\n"
        f"Due Date: {task['dates'].get('due', 'N/A')}\n"
        f"Permalink: {task['permalink']}\n"
        f"Priority: {task['priority']}\n"
        f"Assignee: {get_user_details(task.get('responsibleIds')[0])}\n"
    )
    task_details += "---------------------------------\n"
    return task_details

# Function to print tasks fetched from Wrike
def print_tasks(tasks):
    for task in tasks:
        print(format_task(task))

# MAIN
if __name__ == '__main__':
    try:
        folder_id = get_folder_id()  # Fetch folder ID dynamically
        migrate_tasks()
    except Exception as e:
        print(f"An error occurred in main: {e}")
    finally:
        print("Execution completed.")
