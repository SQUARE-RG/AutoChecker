template <typename... Ts>
void ignore(Ts... args) {
    (void)(sizeof...(args));
}

int main() {
    ignore(1, 2.0, 'c');
    return 0;
}
