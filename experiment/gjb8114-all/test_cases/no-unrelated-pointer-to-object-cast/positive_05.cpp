#include <iostream>

class Session {
public:
    Session() : token(7) {}
    int token;
};

int main() {
    Session *original = new Session();
    void *raw = original;
    Session *restored = reinterpret_cast<Session*>(raw);
    std::cout << restored->token << std::endl;
    delete original;
    return 0;
}
