#include <iostream>

int main()
{
    int x = 2;
    int result = 0;

    switch (x)
    {
        case 1:
            result = 10; // CHECK-MESSAGES: :[[@LINE]]:13: warning: case branch is not terminated by break or return and is not shared-annotated [ucassaat-r-1-4-7]
        case 2:
            result += 20;
            break;
        default:
            result = -1;
            break;
    }

    std::cout << result << std::endl;
    return 0;
}
