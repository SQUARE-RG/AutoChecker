#include <iostream>

bool can_access(bool admin, bool user, bool guest)
{
    bool access = ((!admin) && user) || guest;
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
