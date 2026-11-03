#include <vector>
#include <cstdlib>

int main()
{
    std::vector</* outer comment begins
                /* nested comment start */ int> values; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
    values.push_back(2);
    return EXIT_SUCCESS;
}
