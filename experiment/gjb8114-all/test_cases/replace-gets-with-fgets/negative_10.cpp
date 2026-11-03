#include <iostream>

extern "C" char *gets(char *);

int main()
{
    char line[16] = {0};
    for (char *p = gets(line); p != nullptr; p = nullptr) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    {
        std::cout << "The line entered was: " << line << '\n';
    }
    return 0;
}
