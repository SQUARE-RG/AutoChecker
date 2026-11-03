#include <iostream>

bool can_access(bool admin, bool user, bool guest)
{
    bool access = !admin && user || guest; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-4]
    return access;
}

int main()
{
    bool admin = false;
    bool user = true;
    bool guest = false;
    bool result = can_access(admin, user, guest);
    std::cout << result << std::endl;
    return 0;
}
