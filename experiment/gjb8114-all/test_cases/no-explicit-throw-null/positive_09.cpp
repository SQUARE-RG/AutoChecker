#include <iostream>
using namespace std;

int main(void)
{
    try
    {
        throw 1;
    }
    catch (int value)
    {
        cout << value << endl;
    }
    return 0;
}
