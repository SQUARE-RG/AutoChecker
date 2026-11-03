#include <iostream>
using namespace std;

class A1 {
public:
    A1() {}
};

class A2 {
public:
    A2() {}
};

int main() {
    int i = 0;
    try {
        if (i > 0) {
            throw A1();
        } else {
            throw A2();
        }
    } catch (A2 &) {
        cout << "exception:A2" << endl;
    } catch (A1 &) {
        cout << "exception:A1" << endl;
    }
    return 0;
}
