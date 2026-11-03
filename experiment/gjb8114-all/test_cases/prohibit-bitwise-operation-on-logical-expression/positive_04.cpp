bool check(bool a, bool b) {
    bool result = !(a && b);
    return result;
}

int main() {
    return check(true, false) ? 0 : 1;
}
