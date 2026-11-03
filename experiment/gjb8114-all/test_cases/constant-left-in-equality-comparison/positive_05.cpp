bool is_enabled(bool flag) {
    return true == flag;
}

int main() {
    return is_enabled(false) ? 0 : 1;
}
