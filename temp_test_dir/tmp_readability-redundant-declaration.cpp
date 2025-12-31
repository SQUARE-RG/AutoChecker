// File: negative_struct_member.c
#include <stdlib.h>
struct Container {
    int *data_ptr;
};
void test_struct(void) {
    struct Container c;
    c.data_ptr = (int*)malloc(sizeof(int));
    *(c.data_ptr) = 42; 
    //
}