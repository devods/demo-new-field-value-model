# New Field Value By User Model
The model tracks new field value that occurs within 1 day by entity id.
# Use cases
1. Tracking places users have never been before in an organization.
2. Tracking new ip addressses users accesses in an organization.
3. Tracking new machines types that ip addresses register in a network.

> The model identifies new values only within 1 day from running time. The model should be set up with enough lead time to build database though. For example, you can start the model 30 days from now to start tracking new values from yesterday.

# Set up
1. Go to model server and create a new model.
2. Put in the model's image address <will be provided by us>.
3. Enter read/write credentials on your domain.
4. Set a model start time.
5. Configure query: makre sure to contain 3 fields: eventdate, analyzedField, entityId

```SQL
from {table}
{other operations}
select
    eventdate,
    {field you want to track} as analyzedField,
    {field for user/entity identification} as entityId
```

example
```SQL
from siem.logtrust.web.activity
    group every 5m by country, username
    select country as analyzedField, username as entityId
```
6. Submit to model server and start.

# output
The model will write to the output you set with the following message format
```JSON
{"entity_id": {the user/entity id}, "lastmodifieddate": {the timestmap the new finding is seen}, "new_value": {the new value found}}
```
