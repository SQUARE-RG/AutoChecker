#include <iostream>
using namespace std;

typedef int Arr10[10];

void fun(Arr10& p)
{
    for (int i = 0; i < 10; ++i) {
        p[i] += 1;
    }
}

int main() {
    Arr10 a = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};
    fun(a);
    return 0;
}
