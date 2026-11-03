#include <iostream>

struct Status
{
    unsigned int code;
};

int main()
{
    Status status{1};
    int result = 0;
    switch (status.code)
    {
        case 1:
            result = 10;
            break;
        case 2:
            result = 20;
            break;
        default:
            result = 0;
            break;
    }
    std::cout << result << '\n';
    return 0;
}
