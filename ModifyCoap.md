# Modify libCoAP library
In order to change the .well-known core URI we had to modify the libcoap library
[Based on the tutorial here](https://docs.google.com/document/d/10DpC5AZmfksBenXDyYCO-mwZvB9SxzlF7hFYtvHeX9Y/edit)

## The pycom-micropthon-sigfox

File ***esp32/mods/modcoap.c***
Add this:
```code
// --- Our modification ----
STATIC const mp_arg_t mod_coap_our_function_args[] = {
    	{ MP_QSTR_uri,                  	MP_ARG_REQUIRED | MP_ARG_OBJ, }
};

// Call coap_ourfunction
STATIC mp_obj_t mod_coap_our_function(mp_uint_t n_args, const mp_obj_t *pos_args, mp_map_t *kw_args) {

	// The Coap module should have been already initialized
	if (initialized == true) {
    	// Take the context's semaphore to avoid concurrent access, this will guard the handler functions too
    	xSemaphoreTake(coap_obj_ptr->semphr, portMAX_DELAY);
   	 
    	// We parse the parameters, there will be only one in our case
    	mp_arg_val_t args[MP_ARRAY_SIZE(mod_coap_our_function_args)];
    	mp_arg_parse_all(n_args, pos_args, kw_args, MP_ARRAY_SIZE(args), mod_coap_our_function_args, args);

   	 
    	// Here we call our function in libcoap (no return value in this example):
        // to test, this is the way we convert a micropython string objet to a a C char array,
        // libcoap internally will use  uint8_t *s , but is equivalent. Maybe the conversion should be done here ? (uint8_t*)
    	const char* uri = mp_obj_str_get_str(args[0].u_obj); 
   	 
    	coap_change_wellknown_uri( uri );
   
    	xSemaphoreGive(coap_obj_ptr->semphr);
	}
	else {
    	nlr_raise(mp_obj_new_exception_msg(&mp_type_RuntimeError, "Error, the module is not modified!\n Trying to modify the CoAP .well-known/core URI! :´("));
	}

	return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_KW(mod_coap_our_function_obj, 1, mod_coap_our_function);

```

... and this:
```code
STATIC const mp_map_elem_t mod_coap_globals_table[] = {
    ...
    { MP_OBJ_NEW_QSTR(MP_QSTR_ourfunction),                     (mp_obj_t)&mod_coap_ourfunction_obj }, 
    ...
}
```

## The Pycom-ESP-IDF tool
### Net.c
In the ***components/coap/libcoap*** directory modify the ***src/net.c*** file.

Currently 16 chars, same as the URI

On line 313, modify to this:

```code

char coap_default_uri_wellknown[16] = ".well-known/core";

void coap_change_wellknown_uri(const char *uri) {
    /* Copies the uri to the coap default uri, */
    /* TODO: byte zero in case of different length?*/
    strcpy(coap_default_uri_wellknown, uri);
}

/** Checks if @p Key is equal to the pre-defined hash key for.well-known/core. */
int is_wkc(coap_key_t k) {
  static coap_key_t wkc;
  static unsigned char _initialized = 0;

  // Always create the hash, since we could change
  _initialized = coap_hash_path((unsigned char *)coap_default_uri_wellknown, 
        sizeof(coap_default_uri_wellknown), wkc);

  // Check if same
  return memcmp(k, wkc, sizeof(coap_key_t)) == 0;
}

```
### Net.h
In the ***include/coap/net.h*** on line 521.
```code
 */
coap_pdu_t *coap_wellknown_response(coap_context_t *context,
                                    coap_pdu_t *request);


/** Add this code below **/

/**
* Our custom function to change .well-known/core URI
*
* @param uri  	Char array for the new URI (same length as defail)
*/
void coap_change_wellknown_uri(const char *uri);

/** Add this code above **/



#endif /* _COAP_NET_H_ */
```

## Done editing
Follow the steps III and IV again [here](IANVSLoPyBuild.md)

Afterwards, when connected the Pycom device, verify that the created function exists!
```code
from network import Coap

for x in dir(Coap):
   print(x)
```

And hopefully you will see "our_function" is there!
```code
Coap.our_function(".secret-core/hey")
```

Test:
```terminal
coap-client -m get coap://192.168.1.10:7000/.secret-core/hey
```