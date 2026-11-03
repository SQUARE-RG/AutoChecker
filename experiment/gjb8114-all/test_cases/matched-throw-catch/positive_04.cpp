class A {};

int main() {
    try {
        throw A();
    } catch (const A&) {
    }
    return 0;
}
