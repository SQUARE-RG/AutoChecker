#include <cstdlib>

enum Color
{
    RED,
    GREEN = 'G', // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-4]
    BLUE
};

int main()
{
    Color c = BLUE;
    (void)c;
    return EXIT_SUCCESS;
}
