#include <cstring>

class A {
public:
    A(const char* s) : str(new char[20]) {
        std::strncpy(str, s, 19);
        str[19] = 0;
    }
    A(const A& other) : str(new char[20]) {
        std::strncpy(str, other.str, 19);
        str[19] = 0;
    }
    ~A() { delete[] str; }
    A& operator=(const A&) = delete; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
private:
    char* str;
};

int main() {
    char text[2] = {'x', 0};
    A a(text);
    A b(a);
    return 0;
}
