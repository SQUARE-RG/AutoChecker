#include <string>

std::string make_name(int id);

int main()
{
    std::string name = make_name(3);
    return name.empty() ? 1 : 0;
}

std::string make_name(int id)
{
    std::string base = "item-";
    base += std::to_string(id);
    return base;
}
