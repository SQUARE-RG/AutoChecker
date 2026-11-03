#include <cstdlib>

int classify(int value);

int main(void)
{
    return classify(2);
}

int classify(int value)
{
    switch (value)
    {
    case 0:
        return 10;
    case 1:
        return 20;
    }
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]
