#include <cstring>

class A {
public:
    A(const char* s) : str(new char[20]) {
        std::strncpy(str, s, 19);
        str[19] = 0;
    }
    A(const A&) = delete; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-1]
    ~A() { delete[] str; }
    A& operator=(const A& other) {
        if (this != &other) {
            char* next = new char[20];
            std::strncpy(next, other.str, 19);
            next[19] = 0;
            delete[] str;
            str = next;
        }
        return *this;
    }
private:
    char* str;
};

int main() {
    char text[2] = {'x', 0};
    A a(text);
    A b(text);
    b = a;
    return 0;
}
