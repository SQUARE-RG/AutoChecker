#include <iostream>

int main()
{
    bool ready = true;
    bool started = false;
    int state = 0;
    switch (ready && started) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
        case 1:
            state = 1;
            break;
        case 0:
            state = 2;
            break;
    }
    return state;
}
