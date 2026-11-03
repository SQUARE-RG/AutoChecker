#include <iostream>

typedef struct DataPoint
{
    int x;
    int y;
} DataPoint;

int main()
{
    int DataPoint = 10; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-6]
    std::cout << DataPoint << std::endl;
    return 0;
}
