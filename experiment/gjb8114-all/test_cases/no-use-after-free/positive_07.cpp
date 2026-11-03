#include <list>

int main()
{
    std::list<int> values{1, 2, 3};
    int *pointer = &values.back();
    int result = *pointer;
    values.pop_back();
    return result;
}
