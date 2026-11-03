#include <iostream>

extern "C" char *gets(char *);

int main()
{
    char line[16] = {0};
    if (char *p = gets(line); p != nullptr) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-18]
    {
        std::cout << "The line entered was: " << line << '\n';
    }
    else
    {
        std::cerr << "gets error\n";
        return 1;
    }
    return 0;
}
