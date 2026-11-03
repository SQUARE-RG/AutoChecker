#include <cstddef>

static int global_value = 7;

void assign_in_switch(int* target, int mode)
{
    switch (mode) {
    case 0:
        break;
    case 1:
        target = &global_value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-3]
        break;
    default:
        break;
    }
    (void)target;
}
