#include <exception>
#include <stdexcept>

int main() {
    try {
        throw 42;
    } catch (const std::exception&) {
        return 1;
    } catch (int) {
        return 2;
    } catch (...) {
        return 3;
    }
    return 0;
}
