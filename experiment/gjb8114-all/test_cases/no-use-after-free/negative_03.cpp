#include <iostream>

void release(int* p)
{
    delete p;
}

int main()
{
    int* value = new int(42);
    release(value);
    int read = *value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    std::cout << read << '\n';
    return 0;
}
