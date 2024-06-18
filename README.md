### wsgi-base

- When compiling a URL map, in addition to the embedded ones (str, int, float), it is possible to use patterns constructed using regular expressions.

- Routing has the functions of assembling URLs using patterns from routes and static URLs for files.

- When start processing a request in the utility, utc starts with the variables: "now" date and time with the UTC time zone and "timestamp" as a floating point number. Has built-in delta to offset the time zone of the date and time provided to it, as well as the timestamp.

- The assembly includes parsers for incoming requests, cookies, information from forms (including files uploaded to the server) and are implemented into the functionality of the incoming request.

- The assembly contains controls for HTTP headers, request redirection, and cookies. Has a template engine that includes individual functions from the http set and processing of the context passed to it. The context in the template engine can be processed using built-in functions.

- The framework allows you to add your own 404 error handler.

- You can send a file or redirect the request as a response.
