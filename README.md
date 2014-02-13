# Pupa: A legislative data scraping framework

## Popolo

Pupa implements the Person, Organization, Membership and Post models from the [Popolo data specification](http://popoloproject.com/). Notably, it:

* does not implement an `id` property, instead using `_id` from MongoDB, with the exception of the `id` property on the Post model
* does not implement [name components](http://popoloproject.com/specs/person/name-component.html) on the Person model
* does not implement a top-level `email` property on the Person model, instead using the `contact_details` property for all contact information
* does not implement a `sources` property on the Membership model
* does not implement `created_at`, `updated_at` or `sources` properties on the Post model
* requires the `name` property on the Person and Organization models, and the `label` property on the Post model
* does not implement [embedded JSON documents](http://popoloproject.com/specs/#embedded-json-documents), with the exception of the `posts` property on the Organization model
