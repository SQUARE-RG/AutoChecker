#include <map>

int main()
{
    std::map<int, int> values;
    values[1] = 10;
    int *pointer = &values[1];
    int result = *pointer;
    values.erase(1);
    return result;
}
