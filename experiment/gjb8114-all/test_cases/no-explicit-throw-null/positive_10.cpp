#include <iostream>
using namespace std;

int main(void)
{
    bool high = true;
    try
    {
        throw high ? 10 : 20;
    }
    catch (int value)
    {
        cout << value << endl;
    }
    return 0;
}
