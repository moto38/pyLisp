# pyLisp
オールPython製の純Lisp+アルファな何か。ただし仕様はSchemeのほうを参考にしている。ので、LispよりSchemeもどきといったほうが近いかもしれない。

- 内部的にconsセルでデータをもっています。
- 評価は適正順
- 再帰可能
- 外部ファイルのロード機能あり
- 仕様の大きさ的には純Lisp程度
- 循環定義は実装予定




実装済み機能

- cons / car / cdr
- atom
- eq
  - オブジェクト比較ではなく値比較
- < / >
- 四則演算
  - 割り算は小数返すpython依存
- if / cond
  - ex. (if (func) (procT) (procNil)
- t / nil
- lambda
  - ex. (lambda (x y) (+ x y))
- define
  - ex. (define a 1)
  - ex. (define f (lambda (n) (+ n 1)))
- set!
  ローカルシンボル定義
  使い方は define と一緒
- and / or
- quote
- シンボルテーブル参照
  - ex. グローバル (showtab)
  - ex. ローカル (showlocal f)





  
