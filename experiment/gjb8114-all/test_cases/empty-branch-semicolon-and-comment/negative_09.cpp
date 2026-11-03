#include <iostream>

int main()
{
    bool ready = true;
    int result = 0;
    if (ready) { ;/* no deal with */ } else { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]
        result = 7;
    }
    std::cout << result << std::endl;
    return 0;
}
