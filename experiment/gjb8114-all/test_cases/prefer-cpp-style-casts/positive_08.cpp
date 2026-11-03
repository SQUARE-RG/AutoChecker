using Func = void (*)(int);

int main() {
    auto lambda = [](int) {};
    Func f = static_cast<Func>(lambda);
    f(42);
    return 0;
}
