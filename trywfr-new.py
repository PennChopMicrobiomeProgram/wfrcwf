from wfrcwflib.workflow import (
    Workflow, Step,
    PositionalArgument, OptionalArgument,
    InputConnector, OutputConnector,
    OutputPrefixConnector, InputPrefixConnector,
    OutputStdoutConnector,
)

s1 = Step("bwa-index", "bwa")
s1.args.append(PositionalArgument("index"))
s1.args.append(OptionalArgument("-p", [OutputPrefixConnector(".bwt")]))
s1.args.append(PositionalArgument(InputConnector(".fasta")))

s2 = Step("bwa-align", "bwa")
s2.args.append(PositionalArgument("mem"))
s2.args.append(PositionalArgument(InputPrefixConnector(".bwt")))
s2.args.append(PositionalArgument(InputConnector(".fastq")))
s2.stdout = OutputStdoutConnector(".sam")

w = Workflow("bwa-search", {"bwa-index": s1, "bwa-align": s2})
w.connect("bwa-index", ".bwt", "bwa-align", ".bwt")
print(w.connections_in)
print("Inputs:", list(w.inputs))
print(w.connections_out)
print("Outputs:", list(w.outputs))

# f1 = WorkflowFile(Path("."), "sample1", ".fastq")
# f2 = WorkflowFile(Path("."), "phix174", ".fasta")
# c1 = RunnableCommand(s1, Path("output", {".fasta": f2}))
# print(c1.output_basename)
# print(c1.output_files)

# x = Step("say hello", "echo")
# x.args.append(PositionalArgument("hello"))
# x.args.append(PositionalArgument("world"))
# print(x)

# x2 = Step("read_file", "cat")
# x2.args.append(PositionalArgument(InputConnector("f", ".txt")))
# print(x2)
# print(list(x2.inputs))

# c1 = Step("copy_1", "cp")
# c1.args.append(PositionalArgument(InputConnector("source", ".toml")))
# c1.args.append(PositionalArgument(OutputConnector("dest", ".txt")))

# c2 = Step("copy_2", "cp")
# c2.args.append(PositionalArgument(InputConnector("source", ".txt")))
# c2.args.append(PositionalArgument(OutputConnector("dest", ".config")))

# w = Workflow([c1, c2])
# print(list(w.inputs))
# print(list(w.outputs))

# w.connect("copy_1", "dest", "copy_2", "source")
# print("Connections in:", w.connections_in)
# print("Inputs:", list(w.inputs))
# print("Connections out:", w.connections_out)
# print("Outputs:", list(w.outputs))

# print(w.dag)
# print(list(w.edges))


# csv_filetype = SuffixedFiletype("csv", ".csv")
# fasta_filetype = SuffixedFiletype("fasta", ".fasta", [".fna", ".fa"])
# fastq_r1 = SuffixedFiletype("r1", "_R1.fastq")
# fastq_r2 = SuffixedFiletype("r2", "_R2.fastq")
# paired_fastq_filetype = SuffixedFiletypeBundle("paired-fastq", (fastq_r1, fastq_r2))

# registry = FiletypeRegistry()
# registry.register(csv_filetype)
# registry.register(fasta_filetype)
# registry.register(paired_fastq_filetype)
# print(registry["fasta"])
# print(registry["paired-fastq"])

#input_fp = Path("pyproject.toml")
#p = Project(w, {}, {("copy_1", "source"): input_fp}, "myoutput")

# step copy_1
#   cp
#   { input source toml }
#   { output dest txt }

# step copy_2
#   cp
#   { input source txt }
#   { output dest config }

# workflow double_copy
#   copy_1 dest -> copy_2 source

# step blastn_genes
#   blastn
#   -db {input db blastndb}
#   -in {input seqs fasta}
#   -evalue 1e-5

# configure blastn_genes
#   -evalue 1e-3

#try:
#    x2.run()
#except Exception as e:
#    print(e)
#x2.set_input("f", "pyproject.toml")
#print(x2.inputs)
#print(x2.argv)
#x2.run()
