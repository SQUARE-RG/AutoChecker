#include <iostream>

class Document {
public:
    int docid;
    Document() : docid(0) {}
    explicit Document(int v) : docid(v) {}
};

class Book : public Document {
public:
    int bookid;
    template <typename T>
    explicit Book(T v) : bookid(static_cast<int>(v)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-5]
    {}
};

int main() {
    Book mybook(42);
    std::cout << mybook.docid << mybook.bookid << std::endl;
    return 0;
}
