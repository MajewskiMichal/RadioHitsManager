RadioHitsManager
================

Flask RESTful api implementing CRUD for managing radio hits and authors. 

# Running

When you are in docker-compose.yml directory, this repo can be run by typing:

``` bash
$ docker-compose up
```

### Get the list of 20 latest hits:

**Definition**

`GET /api/v1/hits`

Example Responses:-
     
On Success: status: 200
     
 ```
    [
    {
        "id": 1,
        "title": "Betonowy Las",
        "title_url": "Betonowy-Las"
    },
    {
        "id": 2,
        "title": "Some example",
        "title_url": "Some-example"
    }
    ]
     
```

### Get hit details 

**Definition**

`GET /api/v1/hits/{title_url}`

Example Responses:-
     
On Success: status: 200
     
     
```
{
    "artist": {
        "first_name": "Justyna",
        "id": 5,
        "last_name": "Swies"
    },
    "hit": {
        "id": 3,
        "title": "Betonowy",
        "title_url": "Betonowy"
    }
}
```

On error: status: 404
    
    ```
    {
        "error": "This title doesn't exist"
    }
    ``` 
    
### Create hit 

**Definition**

`POST /api/v1/hits`

**Request body**
```
{
	"artist_id": 99,
	"title": "Some Title"
}
```

Example Responses:-
     
On Success: status: 201

```
{
    "id": 162,
    "title": "Some Title",
    "title_url": "Some-Title"
}

```

**Request body**
```
{
	"artist_id": 99,
	"title": "Some#@& Title"
}
```

On error: status: 400
    
    ```
 {
    "error": "title must be a non empty string containing only letters ans spaces"
 }
    ``` 
### Update Hit

**Definition**

`PUT /api/v1/hits/{title_url}` 

**Request body**
```
{
	"title": "New Title"
}
```

Example Responses:-
     
On Success: status: 201

```
{
    "id": 162,
    "title": "New Title",
    "title_url": "New-Title"
}

```

On error: status: 404
    
```
 {
    "error": "This title doesn't exist"
 }
```

### Delete Hit

**Definition**

`DELETE /api/v1/hits/{title_url}`


Example Responses:-

On Success: status: 202


```{
    "id": 46,
    "title": "Some Title",
    "title_url": "Some-Title"
    }
```

On error: status: 404
    
```
 {
    "error": "This title doesn't exist"
 }
```

### Unit Tests
This repo is configured to be unit tested with pytest

```bash
$ pytest --cov-report term-missing --cov=./

```

    
    










