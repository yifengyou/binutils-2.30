
# Determine if this is a native build or a cross build.
#
# For a cross build add  --define "binutils_target <target>" to the command
# line when building the rpms.
#
# For example:
#  --define "binutils_target aarch64-linux-gnu"
#
# Cross builds will create a set of binutils executables that will run on the
# host machine but which will create binaries suitable for running on the
# target machine.  The cross tools will have the target name as a prefix,
# but for compatibility with the kernel the rpms will use the target name
# as an infix.  So for example building with the above define will create a
# set of rpms like this:
#
#   binutils-aarch64-linux-gnu-2.35.1-14.fc34.x86_64.rpm
#   binutils-aarch64-linux-gnu-debuginfo-2.35.1-14.fc34.x86_64.rpm
#   [etc]
#
# and the rpms will contain files like:
#
#   /usr/bin/aarch64-linux-gnu-addr2line
#   /usr/bin/aarch64-linux-gnu-ar
#   /usr/bin/aarch64-linux-gnu-as
#   [etc]

%if 0%{!?binutils_target:1}

%define binutils_target %{_target_platform}
%define isnative      1
%define enable_shared 1

%else

%define cross       %{binutils_target}-
%define name_cross -%{binutils_target}
%define isnative      0
%define enable_shared 0

%endif

Summary: A GNU collection of binary utilities
Name: binutils%{?name_cross}%{?_with_debug:-debug}
Version: 2.30
Release: 113%{?dist}
License: GPLv3+
URL: https://sourceware.org/binutils

#----------------------------------------------------------------------------

# Binutils SPEC file.  Can be invoked with the following parameters to change
#  the default behaviour:

# --define "binutils_target arm-linux-gnu" to create arm-linux-gnu-binutils.
#
# --with bootstrap       Build with minimal dependencies.
# --with debug           Build without optimizations and without splitting
#                         the debuginfo into a separate file.
# --without docs         Skip building documentation.
#                         Default is with docs, except when building a cross binutils.
# --without testsuite    Do not run the testsuite.  Default is to run it.
# --without gold         Disable building of the GOLD linker.
# --with clang           To force building with the CLANG.
# --without debuginfod   Disable support for debuginfod.

#---Start of Configure Options-----------------------------------------------

# Create deterministic archives (ie ones without timestamps).
# Default is off because of BZ 1195883.
%define enable_deterministic_archives 0

# Enable support for GCC LTO compilation.
# Disable if it is necessary to work around bugs in LTO.
%define enable_lto 1

# Enable the compression of debug sections as default behaviour of the
# assembler and linker.  This option is disabled for now.  The assembler and
# linker have command line options to override the default behaviour.
%define default_compress_debug 0

# Default to read-only-relocations (relro) in shared binaries.
# This is enabled as a security feature.
%define default_relro 1

# Enable the default generation of GNU Build notes by the assembler.
# This option is disabled as it has turned out to be problematic for the i686
# architecture, although the exact reason has not been determined.  (See
# BZ 1572485).  It also breaks building EFI binaries on AArch64, as these
# cannot have relocations against absolute symbols.
%define default_generate_notes 0

# Enable thread support in the GOLD linker (if it is being built).  This is
# particularly important if plugins to the linker intend to use threads
# themselves.  See BZ 1636479 for more details.  This option is made
# configurable in case there is ever a need to disable thread support.
%define enable_threading 1

#----End of Configure Options------------------------------------------------

# Default: Not bootstrapping.
%bcond_with bootstrap
# Default: Not debug
%bcond_with debug
# Default: Always build documentation.
%bcond_without docs
# Default: Always run the testsuite.
%bcond_without testsuite
# Default: Build the gold linker.
%bcond_without gold

%if %{with bootstrap}
%undefine with_docs
%undefine with_testsuite
%endif

%if %{with debug}
%undefine with_testsuite
%endif

# BZ 1924068.  Since applications that use the BFD library are
# required to link against the static version, ensure that it retains
# its debug informnation.
%undefine __brp_strip_static_archive

#----------------------------------------------------------------------------

# Note - the Linux Kernel binutils releases are too unstable and contain
# too many controversial patches so we stick with the official FSF version
# instead.

Source: https://ftp.gnu.org/gnu/binutils/binutils-%{version}.tar.xz
Source2: binutils-2.19.50.0.1-output-format.sed

%if %{with docs}
# Strictly speaking this next file is not part of the binutils distribution.
# But the emacs info system expects it to be present on any system where
# emacs is installed, and old binutils distributions used to include it by
# mistake.  Since there is no suitable documentation files component to
# current RHEL releases, it is included here instead.  In order to save time
# and complexity it is stored as a pre-built, compressed, info file.
# The upstream version of the original source file can be found here:
#   http://git.savannah.gnu.org/gitweb/?p=gnulib.git;a=blob_plain;f=doc/standards.texi;hb=HEAD
# For more information see: https://bugzilla.redhat.com/show_bug.cgi?id=1467390
Source3: standards.info.gz
%endif

#----------------------------------------------------------------------------

# Purpose:  Use /lib64 and /usr/lib64 instead of /lib and /usr/lib in the
#           default library search path of 64-bit targets.
# Lifetime: Permanent, but it should not be.  This is a bug in the libtool
#           sources used in both binutils and gcc, (specifically the
#           libtool.m4 file).  These are based on a version released in 2009
#           (2.2.6?) rather than the latest version.  (Definitely fixed in
#           libtool version 2.4.6).
Patch01: binutils-2.20.51.0.2-libtool-lib64.patch

# Purpose:  Appends a RHEL or Fedora release string to the generic binutils
#           version string.
# Lifetime: Permanent.  This is a RHEL/Fedora specific patch.
Patch02: binutils-2.25-version.patch

# Purpose:  Exports the demangle.h header file (associated with the libiberty
#           sources) with the binutils-devel rpm.
# Lifetime: Permanent.  This is a RHEL/Fedora specific patch.
Patch03: binutils-2.22.52.0.1-export-demangle.h.patch

# Purpose:  Disables the check in the BFD library's bfd.h header file that
#           config.h has been included before the bfd.h header.  See BZ
#           #845084 for more details.
# Lifetime: Permanent - but it should not be.  The bfd.h header defines
#           various types that are dependent upon configuration options, so
#           the order of inclusion is important.
# FIXME:    It would be better if the packages using the bfd.h header were
#           fixed so that they do include the header files in the correct
#           order.
Patch04: binutils-2.22.52.0.4-no-config-h-check.patch

# Lifetime: Permanent, but needs continual updating.
# FIXME:    Try removing....
Patch05: binutils-2.26-lto.patch

# Purpose:  Include the filename concerned in readelf error messages.  This
#           makes readelf's output more helpful when it is run on multiple
#           input files.
# Lifetime: Permanent.  This patch changes the format of readelf's output,
#           making it better (IMHO) but also potentially breaking tools that
#           depend upon readelf's current format.  Hence it remains a local
#           patch.
Patch06: binutils-2.29-filename-in-error-messages.patch

# Purpose:  Use the "unsigned long long" type for pointers on hosts where
#           long is a 32-bit type but pointers are a 64-bit type.  Necessary
#           because the rpmdiff tester insists that if both the i686 and
#           x86_64 versions of binutils-devel are installed on the same
#           machine, then they will have identical versions of the bfd.h
#           header file.
# Lifetime: Permanent.
Patch07: binutils-2.25-set-long-long.patch

# Purpose:  Changes readelf so that when it displays extra information about
#           a symbol, this information is placed at the end of the line.
# Lifetime: Permanent.
# FIXME:    The proper fix would be to update the scripts that are expecting
#           a fixed output from readelf.  But it seems that some of them are
#           no longer being maintained.
Patch08: binutils-readelf-other-sym-info.patch

# Purpose:  Do not create PLT entries for AARCH64 IFUNC symbols referenced in
#           debug sections.
# Lifetime: Permanent.
# FIXME:    Find related bug.  Decide on permanency.
Patch09: binutils-2.27-aarch64-ifunc.patch

# Purpose:  Remove support for inserting PowerPC Speculation Barrier
#           instructions from the linker.  (It has been deprecated in
#           favour of a hardware fix).
# Lifetime: Fixed in 2.30.1 and/or 2.31.
Patch10: binutils-revert-PowerPC-speculation-barriers.patch

# Purpose:  Stop readelf/objdump for searching for DWO links unless
#           explicitly requested by the user.
# Lifetime: Fixed in 2.30.1 and/or 2.31.
Patch11: binutils-skip-dwo-search-if-not-needed.patch

# Purpose:  Fix a bug in the BFD linker's layout algorithm which ended up
#           placing executable and non-executable pages in the same segment.
# Lifetime: Fixed in 2.30.1 and/or 2.31.
Patch12: binutils-page-to-segment-assignment.patch

# Purpose:  Fix a bug in ld for linking against AARCH64 UEFI
# Lifetime: Fixed in 2.30.1 and/or 2.31
Patch13: binutils-2.30-allow_R_AARCH64-symbols.patch

# Purpose:  Stop strip from replacing unknown relocs with null relocs.  Make
#           it return an error status and not strip the file instead.
# Lifetime: Fixed in 2.31.
Patch14: binutils-strip-unknown-relocs.patch

# Purpose:  Improves objdump's function for locating a symbol to match a
#           given address, so that it uses a binary chop algorithm.
# Lifetime: Fixed in 2.31.
Patch15: binutils-speed-up-objdump.patch

# Purpose:  Ignore duplicate indirect symbols generated by GOLD.
# Lifetime: Permanent.
# FIXME:    This problem needs to be resolved in the FSF sources, but the
#           GOLD maintainers seem to be reluctant to address the issue.
Patch16: binutils-2.28-ignore-gold-duplicates.patch

# Purpose:  Treat relocs against STT_GNU_IFUNC symbols in note sections as
#           if they were relocs against STT_FUNC symbols instead.
# Lifetime: Fixed in 2.31.
Patch17: binutils-ifunc-relocs-in-notes.patch

# Purpose:  Do not discard debug only object files created by GCC v8's
#           LTO wrapper.
# Lifetime: Fixed in 2.31.
Patch18: binutils-debug-section-marking.patch

# Purpose:  Fix the GOLD linker's handling of PROTECTED symbols from the
#           LLVM plugin.
# Lifetime: Fixed in 2.31 (probably - check...).
Patch19: binutils-gold-llvm-plugin.patch

# Purpose:  Enhance the assembler so that it will automatically generate
#           GNU Build attribute notes if none are present in the inputs.
# Lifetime: Fixed in 2.31
Patch20: binutils-gas-build-notes.patch

# Purpose:  Fix a seg-fault triggered by running objdump on a corrupt AOUT
#           format file.
# Lifetime: Fixed in 2.31
Patch21: binutils-CVE-2018-7642.patch

# Purpose:  Fix a seg-fault triggered by running readelf or objdump on a
#           file containing corrupt DWARF debug information.
# Lifetime: Fixed in 2.31
Patch22: binutils-CVE-2018-7643.patch

# Purpose:  Fix a seg-fault triggered by running objdump on a corrupt COFF
#           format file.
# Lifetime: Fixed in 2.31
Patch23: binutils-CVE-2018-7208.patch

# Purpose:  Fix a seg-fault triggered by running readelf or objdump on a
#           file containing corrupt DWARF debug information.
# Lifetime: Fixed in 2.31
Patch24: binutils-CVE-2018-10372.patch

# Purpose:  Fix another seg-fault triggered by running readelf or objdump on a
#           file containing corrupt DWARF debug information.
# Lifetime: Fixed in 2.31
Patch25: binutils-CVE-2018-10373.patch

# Purpose:  Fix a seg-fault triggered by running objcopy on a corrupt ELF
#           file.
# Lifetime: Fixed in 2.31
Patch26: binutils-CVE-2018-7570.patch

# Purpose:  Fix a seg-fault triggered by running objcopy on a large ELF
#           file on a 32-bit host machine.
# Lifetime: Fixed in 2.31
Patch27: binutils-CVE-2018-6323.patch

# Purpose:  Fix a seg-fault triggered by running nm on a corrupt ELF file.
# Lifetime: Fixed in 2.31
Patch28: binutils-CVE-2018-6759.patch

# Purpose:  Fix a seg-fault triggered by running nm on a file containing
#           corrupt DWARF information.
# Lifetime: Fixed in 2.31
Patch29: binutils-CVE-2018-7569.patch

# Purpose:  Fix a seg-fault triggered by running nm on a file containing
#           corrupt DWARF information.
# Lifetime: Fixed in 2.31
Patch30: binutils-CVE-2018-7568.patch

# Purpose:  Fix a seg-fault triggered by running objcopy on a corrupt
#           PE format file.
# Lifetime: Fixed in 2.31
Patch31: binutils-CVE-2018-10534.patch

# Purpose:  Fix a seg-fault triggered by running objcopy on a corrupt
#           ELF format file.
# Lifetime: Fixed in 2.31
Patch32: binutils-CVE-2018-10535.patch

# Purpose:  Have the x86 linker resolve relocations against the _end,
#           __bss_start and -edata symbols locally.
# Lifetime: Fixed in 2.31
Patch33: binutils-x86-local-relocs.patch

# Purpose:  Stop the assembler from generating GNU build notes against
#           linkonce sections.
# Lifetime: Fixed in 2.31
Patch34: binutils-linkonce-notes.patch

# Purpose:  Fix a seg-fault triggered by running objcopy on a corrupt
#           PE format file.
# Lifetime: Fixed in 2.31
Patch35: binutils-CVE-2018-8945.patch

# Purpose:  Fix handling of local version symbols by the x86 linker.
# Lifetime: Fixed in 2.31
Patch36: binutils-x86-local-version.patch

# Purpose:  Fix linker testsuite failures
# Lifetime: Fixed in 2.31 (probably)
Patch37: binutils-fix-testsuite-failures.patch

# Purpose:  Correct warning messages about incompatible PowerPC IEEE
#           long double sizes in different binaries.
# Lifetime: Fixed in 2.31.
Patch38: binutils-PowerPC-IEEE-long-double-warnings.patch

# Purpose:  Fix the generation of relocations for assembler generated notes.
# Lifetime: Fixed in 2.31.
Patch39: binutils-missing-notes.patch

# Purpose:  Fix the gold linker so that it can handle note sections with
#           relocs that refer to discarded code sections.
# Lifetime: Fixed in 2.32 (maybe).
Patch40: binutils-gold-ignore-discarded-note-relocs.patch

# Purpose:  Merge .gnu.build.attribute sections into a single section.
# Lifetime: Fixed in 2.32
Patch41: binutils-merge-attribute-sections.patch

# Purpose:  Remove empty x86 property notes.
# Lifetime: Fixed in 2.31
Patch42: binutils-remove-empty-ISA-properties.patch

# Purpose:  Improve objcopy's --merge-notes option.
# Lifetime: Fixed in 2.32
Patch43: binutils-note-merge-improvements.patch

# Purpose:  Fix GOLDs creation of note segments.
# Lifetime: Fixed in 2.31  [Note - see chmod +x below for this patch].
Patch44: binutils-gold-note-segment.patch

# Purpose:  Stop readelf's reports of gaps in build notes - they are unreliable.
# Lifetime: Unknown.
Patch45: binutils-disable-readelf-gap-reports.patch

# Purpose:  Stop the x86_64 linker from optimizing away PLT entries.
# Lifetime: Probably fixed by new configure option in 2.32
Patch46: binutils-x86_64-disable-PLT-elision.patch

# Purpose:  Stop the binutils from statically linking with libstdc++.
# Lifetime: Permanent.
Patch47: binutils-do-not-link-with-static-libstdc++.patch

# Purpose:  Add a .attach_to_group pseudo-op to the assembler for
#           use by the annobin gcc plugin.
# Lifetime: Permanent.
Patch48: binutils-attach-to-group.patch

# Purpose:  Fix a potential buffer overrun when parsing a corrupt ELF file.
# Lifetime: Fixed in 2.32.
Patch49: binutils-CVE-2018-17358.patch

# Purpose:  Make the x86_64 linker produce IBT-enabled TLS stubs.
# Lifetime: Fixed in 2.32.
Patch50: binutils-x86_64-ibt-enabled-tlsdesc.patch

# Purpose:  Have the GOLD linker generate PT_NOTE segments with 8-byte alignment.
# Lifetime: Maybe fixed in 2.32.
Patch51: binutils-gold-8-byte-note-segments.patch

# Purpose:  Add support for disassembling NFP binaries.
# Lifetime: Fixed in 2.31.
Patch52: binutils-nfp.patch

# Purpose:  Add support for the arch13 extension to the s390x architecture.
# Lifetime: Fixed in 2.31.
Patch53: binutils-s390x-arch13.patch

# Purpose:  Add support for partially relocatable GOT sections on the s390x architecture.
# Lifetime: Fixed in 2.31.
Patch54: binutils-s390x-partial-relro.patch

# Purpose:  Do not enable IBT if an object file contains code but no GNU Property notes.
# Lifetime: Fixed in 2.33
Patch55: binutils-x86-IBT-and-missing-notes.patch

# Purpose:  Fixes a problem with the AArch64 port of the GOLD linker.
# Lifetime: Fixed in 2.32
Patch56: binutils-AArch64-gold.patch

# Purpose:  Stop the BFD library from complaining about files with multiple
#           relocations against the same section.  Allows examination of
#           special kernel modules.
# Lifetime: Fixed in 2.33
Patch57: binutils-multiple-relocs-for-same-section.patch

# Purpose:  Stop the linker from merging groups which have different settings
#           of the SHF_EXCLUDE flag.
# Lifetime: Fixed in 2.33
Patch58: binutils-do-not-merge-differing-SHF_EXCLUDE-groups.patch

# Purpose:  Add support for the SVE variant PCS in AArch64.
# Lifetime: Fixed in 2.33
Patch59: binutils-aarch64-STO_AARCH64_VARIANT_PCS.patch

# Purpose:  Add fixes and markers for Coverity test failures.
# Lifetime: Permanent.
Patch60: binutils-coverity-fixes.patch

# Purpose:  Improve objcopy's merging of GNU build attribute notes.
# Lifetime: Fixed in 2.33
Patch61: binutils-improved-note-merging.patch

# Purpose: Add check to readelf in order to prevent an integer overflow.
# Lifetime: Fixed in 2.33
Patch62: binutils-CVE-2019-14444.patch

# Purpose: Fix a seg-fault in gold when linking corrupt input files.
# Lifetime: Fixed in 2.34 (maybe)
Patch63: binutils-CVE-2019-1010204.patch

# Purpose: Add a feature to the x86/64 assembler to create
#           workarounds for the Intel Jcc Erratum.
# Lifetime: Fixed in 2.34
Patch64: binutils-x86_JCC_Erratum.patch

# Purpose:  Fix a potential seg-fault in the BFD library when parsing
#            pathalogical debug_info sections.
# Lifetime: Fixed in 2.34 
Patch65: binutils-CVE-2019-17451.patch

# Purpose:  Fix a memory exhaustion bug in the BFD library when parsing
#            corrupt DWARF debug information.
# Lifetime: Fixed in 2.34 
Patch66: binutils-CVE-2019-17450.patch

# Purpose:  Allow the BFD library to handle the copying of files which
#            contain secondary reloc sections.
# Lifetime: Fixed in 2.35 
Patch67: binutils-copy-multiple-relocs.patch

# Purpose:  Stop the BFD library from issueing warning messages about allocated
#            sections being found outside of loadable segments, if they are
#            found inside debuginfo files.
# Lifetime: Fixed in 2.33
Patch68: binutils-do-not-warn-about-debuginfo-files.patch

# Purpose:  Fix failures in the linker testsuite for the s390-linux target.
# Lifetime: Fixed in 2.33
Patch69: binutils-s390-ld-test-fixes.patch

# Purpose:  Fix failures in the linker testsuite for the s390-linux target.
# Lifetime: Fixed in 2.33
Patch70: binutils-aarch64-ld-test-fixes.patch

# Purpose:  Fix building the binutils with address sanitization enabled.
# Lifetime: Fixed in 2.33
Patch71: binutils-sanitize-uses-dlsym.patch

# Purpose:  Fix building the binutils with address sanitization enabled.
# Lifetime: Fixed in 2.33
Patch72: binutils-PT_GNU_PROPERTY-segment.patch

# Purpose:  Stop gold from aborting when input sections with the same name
#            have different flags.
# Lifetime: 2.33 (probably)
Patch73: binutils-gold-mismatched-section-flags.patch

# Purpose:  Stop objcopy's --set-section-flag option from accepting the
#            'shared' flag on non-COFF binaries.
# Lifetime: Fixed in 2.34
Patch74: binutils-objcopy-set-section-flags-shared.patch

# Purpose:  Prevent the s/390 linker from rewriting the GOT access
#            for certain symbols.
# Lifetime: Fixed in 2.32
Patch75: binutils-s390x-prevent-GOT-rewrite.patch

# Purpose:  Have the s/390 assembler include alignment hints in vector
#           instructions.
# Lifetime: Fixed in 2.35
Patch76: binutils-s390-alignment-hints.patch

# Purpose:  Fix the x86 assembler so that it does not scale non-8-bit
#            displacements.
# Lifetime: Fixed in 2.32
Patch77: binutils-x86-gas-scaled-8-bit-displacements.patch

# Purpose:  Allow plugin syms to mark as-needed shared libs needed.
# Lifetime: Fixed in 2.36
Patch78: binutils-plugin-as-needed.patch

# Purpose:  Fix merging attributes in the presence of multiple
#            same-named sections.
# Lifetime: Fixed in 2.36
Patch79: binutils-strip-merge.patch

# Purpose:  Properly override IR definitions
# Lifetime: Fixed in 2.35
Patch80: binutils-ld-IR-override.patch

# Purpose:  Add support for Intel's TPAUSE and UNWAIT instructions.
# Lifetime: Fixed in 2.31
Patch81: binutils-x86-tpause.patch

# Purpose:  Add support for AArch64 GNU Property notes
# Lifetime: Fixed in 2.34
Patch82: binutils-aarch64-properties.patch

# Purpose:  Fix the version selected when merging common symbols
#            and normal symbols.
# Lifetime: Fixed in 2.36
Patch83: binutils-common-sym-versioning.patch

# Purpose:  Fix merging empty ppc64le notes.
# Lifetime: Fixed in 2.37
Patch84: binutils-ppc64le-note-merge.patch

# Purpose:  Another fix for weak symbol handling with LTO.
# Lifetime: Fixed in 2.36
Patch85: binutils-plugin-as-needed-2.patch

# Purpose:  Fix a potential vulnerability involing symlink overwriting.
# Lifetime: Fixed in 2.37
Patch86: binutils-CVE-2021-20197.patch

# Purpose:  Fix copy relocs that refer to weak aliases
# Lifetime: Fixed in 2.35
Patch87: binutils-mark-all-weak-aliases.patch

# Purpose:  Fix excessive memory consumption when attempting to parse corrupt
#            DWARF debug information.
# Lifetime: Fixed in 2.36
Patch88: binutils-CVE-2021-3487.patch

# Purpose:  Fix illegal memory access when parsing corrupt ELF files.
# Lifetime: Fixed in 2.36
Patch89: binutils-CVE-2020-35448.patch

# Purpose: Fixed heap-based buffer overflow in _bfd_elf_slurp_secondary_reloc_section.
# Lifetime: Fixed in 2.36
Patch90: binutils-CVE-2021-20284.patch

# Purpose: Fixed the handling of relocations against discarded sections.
# Lifetime: Fixed in 2.34
Patch91: binutils-clearing-discarded-relocs.patch

# Purpose: Fix the GOLD linker's generation of .note.gnu.property sections for x86.
# Lifetime: Fixed in 2.37 (maybe)
Patch92: binutils-gold-i386-gnu-property-notes.patch

# Purpose: Fix problems with the binutils-plugin-as-needed.patch
# Lifetime: Fixed in 2.37
Patch93: binutils-plugin-as-needed-correct.patch

# Purpose:  Add support for the arch14 extensions to the s390x architecture.
# Lifetime: Fixed in 2.37
Patch94: binutils-s390x-arch14.patch

# Purpose: Add options to control the display of multibyte characters.  CVE 2021-42574
# Lifetime: Fixed in 2.38 (maybe)
Patch95: binutils.unicode.patch

# Purpose: Make undefined unversioned dynamic symbols global rather than local.
# Lifetime: Fixed in 2.37
Patch96: binutils-undefined-unversioned-symbols.patch

# Purpose: When searching for plugins, do not complain if incompatible ones are found.
# Lifetime: Fixed in 2.35
Patch97: binutils-plugin-error.patch

#----------------------------------------------------------------------------

Provides: bundled(libiberty)
BuildRequires: autoconf automake

%if %{with gold}
%define gold_arches %{ix86} x86_64 %{arm} aarch64 %{power64} s390x
%else
%define gold_arches none
%endif

%if %{with bootstrap}
%define build_gold      no
%else
%ifarch %gold_arches
%define build_gold      both
%else
%define build_gold      no
%endif
%endif

%if %{with debug}
# Define this if you want to skip the strip step and preserve debug info.
# Useful for testing.
%define __debug_install_post : > %{_builddir}/%{?buildsubdir}/debugfiles.list
%define debug_package %{nil}
%endif

Buildroot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

# Perl, sed and touch are all used in the %%prep section of this spec file.
BuildRequires: gcc, perl, sed, coreutils

# Gold needs bison in order to build gold/yyscript.c.
# Bison needs m4.
%if "%{build_gold}" == "both"
BuildRequires: bison, m4, gcc-c++
%endif

%if %{without bootstrap}
BuildRequires: gettext, flex, zlib-devel
%endif

%if %{with docs}
BuildRequires: texinfo >= 4.0
# BZ 920545: We need pod2man in order to build the manual pages.
BuildRequires: /usr/bin/pod2man
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
%else
BuildRequires: findutils
%endif

# Required for: ld-bootstrap/bootstrap.exp bootstrap with --static
# It should not be required for: ld-elf/elf.exp static {preinit,init,fini} array
%if %{with testsuite}
# relro_test.sh uses dc which is part of the bc rpm, hence its inclusion here.
BuildRequires: dejagnu, zlib-static, glibc-static, sharutils, bc
%if "%{build_gold}" == "both"
# The GOLD testsuite needs a static libc++
BuildRequires: libstdc++-static
%endif
%endif

Conflicts: gcc-c++ < 4.0.0

# The higher of these two numbers determines the default ld.
%{!?ld_bfd_priority: %global ld_bfd_priority    50}
%{!?ld_gold_priority:%global ld_gold_priority   30}

%if "%{build_gold}" == "both"
Requires(post): coreutils
Requires(post): %{_sbindir}/alternatives
Requires(preun): %{_sbindir}/alternatives
%endif

# On ARM EABI systems, we do want -gnueabi to be part of the
# target triple.
%ifnarch %{arm}
%define _gnu %{nil}
%endif

#----------------------------------------------------------------------------

%description
Binutils is a collection of binary utilities, including ar (for
creating, modifying and extracting from archives), as (a family of GNU
assemblers), gprof (for displaying call graph profile data), ld (the
GNU linker), nm (for listing symbols from object files), objcopy (for
copying and translating object files), objdump (for displaying
information from object files), ranlib (for generating an index for
the contents of an archive), readelf (for displaying detailed
information about binary files), size (for listing the section sizes
of an object or archive file), strings (for listing printable strings
from files), strip (for discarding symbols), and addr2line (for
converting addresses to file and line).

#----------------------------------------------------------------------------

%package devel
Summary: BFD and opcodes static and dynamic libraries and header files
Provides: binutils-static = %{version}-%{release}
%if %{with docs}
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
%endif
Requires: zlib-devel
Requires: binutils = %{version}-%{release}
# BZ 1215242: We need touch...
Requires: coreutils

%description devel
This package contains BFD and opcodes static and dynamic libraries.

The dynamic libraries are in this package, rather than a separate
base package because they are actually linker scripts that force
the use of the static libraries.  This is because the API of the
BFD library is too unstable to be used dynamically.

The static libraries are here because they are now needed by the
dynamic libraries.

Developers starting new projects are strongly encouraged to consider
using libelf instead of BFD.

# BZ 1924068.  Since applications that use the BFD library are
# required to link against the static version, ensure that it retains
# its debug informnation.
# FIXME: Yes - this is being done twice.  I have no idea why this
# second invocation is necessary but if both are not present the
# static archives will be stripped.
%undefine __brp_strip_static_archive

#----------------------------------------------------------------------------

%prep
%setup -q -n binutils-%{version}
%patch01 -p1
%patch02 -p1
%patch03 -p1
%patch04 -p1
%patch05 -p1
%patch06 -p1
%patch07 -p1
%patch08 -p1
%patch09 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1
%patch27 -p1
%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1
%patch35 -p1
%patch36 -p1
%patch37 -p1
%patch38 -p1
%patch39 -p1
%patch40 -p1
%patch41 -p1
%patch42 -p1
%patch43 -p1
%patch44 -p1
%patch45 -p1
%patch46 -p1
%patch47 -p1
%patch48 -p1
%patch49 -p1
%patch50 -p1
%patch51 -p1
%patch52 -p1
%patch53 -p1
%patch54 -p1
%patch55 -p1
%patch56 -p1
%patch57 -p1
%patch58 -p1
%patch59 -p1
%patch60 -p1
%patch61 -p1
%patch62 -p1
%patch63 -p1
%patch64 -p1
%patch65 -p1
%patch66 -p1
%patch67 -p1
%patch68 -p1
%patch69 -p1
%patch70 -p1
%patch71 -p1
%patch72 -p1
%patch73 -p1
%patch74 -p1
%patch75 -p1
%patch76 -p1
%patch77 -p1
%patch78 -p1
%patch79 -p1
%patch80 -p1
%patch81 -p1
%patch82 -p1
%patch83 -p1
%patch84 -p1
%patch85 -p1
%patch86 -p1
%patch87 -p1
%patch88 -p1
%patch89 -p1
%patch90 -p1
%patch91 -p1
%patch92 -p1
%patch93 -p1
%patch94 -p1
%patch95 -p1
%patch96 -p1
%patch97 -p1

# We cannot run autotools as there is an exact requirement of autoconf-2.59.
# FIXME - this is no longer true.  Maybe try reinstating autotool use ?

# On ppc64 and aarch64, we might use 64KiB pages
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*ppc.c
sed -i -e '/#define.*ELF_COMMONPAGESIZE/s/0x1000$/0x10000/' bfd/elf*aarch64.c
sed -i -e '/common_pagesize/s/4 /64 /' gold/powerpc.cc
sed -i -e '/pagesize/s/0x1000,/0x10000,/' gold/aarch64.cc
# LTP sucks
perl -pi -e 's/i\[3-7\]86/i[34567]86/g' */conf*
sed -i -e 's/%''{release}/%{release}/g' bfd/Makefile{.am,.in}
sed -i -e '/^libopcodes_la_\(DEPENDENCIES\|LIBADD\)/s,$, ../bfd/libbfd.la,' opcodes/Makefile.{am,in}
# Build libbfd.so and libopcodes.so with -Bsymbolic-functions if possible.
if gcc %{optflags} -v --help 2>&1 | grep -q -- -Bsymbolic-functions; then
sed -i -e 's/^libbfd_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' bfd/Makefile.{am,in}
sed -i -e 's/^libopcodes_la_LDFLAGS = /&-Wl,-Bsymbolic-functions /' opcodes/Makefile.{am,in}
fi
# $PACKAGE is used for the gettext catalog name.
sed -i -e 's/^ PACKAGE=/ PACKAGE=%{?cross}/' */configure
# Undo the name change to run the testsuite.
for tool in binutils gas ld
do
  sed -i -e "2aDEJATOOL = $tool" $tool/Makefile.am
  sed -i -e "s/^DEJATOOL = .*/DEJATOOL = $tool/" $tool/Makefile.in
done
touch */configure
# Touch the .info files so that they are newer then the .texi files and
# hence do not need to be rebuilt.  This eliminates the need for makeinfo.
# The -print is there just to confirm that the command is working.
%if %{without docs}
  find . -name *.info -print -exec touch {} \;
%endif

# Not sure how this should be done.  The file is created by
# patch44.
chmod +x gold/testsuite/gnu_property_test.sh

%ifarch %{power64}
%define _target_platform %{_arch}-%{_vendor}-%{_host_os}
%endif

#----------------------------------------------------------------------------

%build
echo target is %{binutils_target}

%ifarch %{power64}
export CFLAGS="$RPM_OPT_FLAGS -Wno-error"
%else
export CFLAGS="$RPM_OPT_FLAGS"
%endif

CARGS=

case %{binutils_target} in i?86*|sparc*|ppc*|s390*|sh*|arm*|aarch64*)
  CARGS="$CARGS --enable-64-bit-bfd"
  ;;
esac

case %{binutils_target} in ia64*)
  CARGS="$CARGS --enable-targets=i386-linux"
  ;;
esac

case %{binutils_target} in ppc*|ppc64*)
  CARGS="$CARGS --enable-targets=spu"
  ;;
esac

case %{binutils_target} in ppc64-*)
  CARGS="$CARGS --enable-targets=powerpc64le-linux"
  ;;
esac

case %{binutils_target} in ppc64le*)
    CARGS="$CARGS --enable-targets=powerpc-linux"
    ;;
esac

# BZ 1920373: Enable PEP support for all targets as the PERF package's
# testsuite expects to be able to read PE format files ragrdless of
# the host's architecture.
case %{binutils_target} in
    s390*)
	# FIXME: For some unknown reason settting --enable-targets=x86_64-pep
	# here breaks the building of GOLD.  I have no idea why, and not enough
	# knowledge of how gold is configured to fix quickly.  So instead I have
	# found that supporting "all" targets works.
	CARGS="$CARGS --enable-targets=all"
	;;
    *)
	CARGS="$CARGS --enable-targets=x86_64-pep"
	;;
esac

%if %{default_relro}
  CARGS="$CARGS --enable-relro=yes"
%else
  CARGS="$CARGS --enable-relro=no"
%endif

%if 0%{?_with_debug:1}
CFLAGS="$CFLAGS -O0 -ggdb2 -Wno-error -D_FORTIFY_SOURCE=0"
%define enable_shared 0
%endif

# BZ 1541027 - include the linker flags from redhat-rpm-config as well.
export LDFLAGS=$RPM_LD_FLAGS

# We could optimize the cross builds size by --enable-shared but the produced
# binaries may be less convenient in the embedded environment.
%configure \
  --quiet \
  --build=%{_target_platform} --host=%{_target_platform} \
  --target=%{binutils_target} \
%ifarch %gold_arches
%if "%{build_gold}" == "both"
  --enable-gold=default --enable-ld \
%else
  --enable-gold \
%endif
%endif
%if %{isnative}
  --with-sysroot=/ \
%else
  --enable-targets=%{_host} \
  --with-sysroot=%{_prefix}/%{binutils_target}/sys-root \
  --program-prefix=%{cross} \
%endif
%if %{enable_shared}
  --enable-shared \
%else
  --disable-shared \
%endif
%if %{enable_deterministic_archives}
  --enable-deterministic-archives \
%else
  --enable-deterministic-archives=no \
%endif
%if %{enable_lto}
  --enable-lto \
%endif
%if %{default_compress_debug}
  --enable-compressed-debug-sections=all \
%else
  --enable-compressed-debug-sections=none \
%endif
%if %{default_generate_notes}
  --enable-generate-build-notes=yes \
%else
  --enable-generate-build-notes=no \
%endif
%if %{enable_threading}
  --enable-threads=yes \
%else
  --enable-threads=no \
%endif
  $CARGS \
  --enable-plugins \
  --with-bugurl=http://bugzilla.redhat.com/bugzilla/

%if %{with docs}
%make_build %{_smp_mflags} tooldir=%{_prefix} all
%make_build %{_smp_mflags} tooldir=%{_prefix} info
%else
%make_build %{_smp_mflags} tooldir=%{_prefix} MAKEINFO=true all
%endif

# Do not use %%check as it is run after %%install where libbfd.so is rebuilt
# with -fvisibility=hidden no longer being usable in its shared form.
%if %{without testsuite}
echo ====================TESTSUITE DISABLED=========================
%else
make -k check < /dev/null || :
echo ====================TESTING=========================
cat {gas/testsuite/gas,ld/ld,binutils/binutils}.sum
%if "%{build_gold}" == "both"
if [ -f gold/test-suite.log ]; then
    cat gold/test-suite.log
fi
if [ -f gold/testsuite/test-suite.log ]; then
    cat gold/testsuite/*.log
fi
%endif
echo ====================TESTING END=====================
for file in {gas/testsuite/gas,ld/ld,binutils/binutils}.{sum,log}
do
  ln $file binutils-%{_target_platform}-$(basename $file) || :
done
tar cjf binutils-%{_target_platform}.tar.xz  binutils-%{_target_platform}-*.{sum,log}
uuencode binutils-%{_target_platform}.tar.xz binutils-%{_target_platform}.tar.xz
rm -f binutils-%{_target_platform}.tar.xz    binutils-%{_target_platform}-*.{sum,log}
%if "%{build_gold}" == "both"
if [-f gold/testsuite/test-suite.log ]; then
  tar cjf  binutils-%{_target_platform}-gold.log.tar.xz gold/testsuite/*.log
  uuencode binutils-%{_target_platform}-gold.log.tar.xz binutils-%{_target_platform}-gold.log.tar.xz
  rm -f    binutils-%{_target_platform}-gold.log.tar.xz
fi
%endif
%endif

#----------------------------------------------------------------------------

%install
%if %{with docs}
%make_install DESTDIR=%{buildroot}
%else
%make_install DESTDIR=%{buildroot} MAKEINFO=true
%endif

%if %{isnative}
%if %{with docs}
make prefix=%{buildroot}%{_prefix} infodir=%{buildroot}%{_infodir} install-info
cp %{SOURCE3} %{buildroot}%{_infodir}
%endif

# Rebuild libiberty.a with -fPIC.
# Future: Remove it together with its header file, projects should bundle it.
%make_build -C libiberty clean
%make_build CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C libiberty

# Rebuild libbfd.a with -fPIC.
# Without the hidden visibility the 3rd party shared libraries would export
# the bfd non-stable ABI.
%make_build -C bfd clean
%make_build CFLAGS="-g -fPIC $RPM_OPT_FLAGS -fvisibility=hidden" -C bfd

# Rebuild libopcodes.a with -fPIC.
%make_build -C opcodes clean
%make_build CFLAGS="-g -fPIC $RPM_OPT_FLAGS" -C opcodes

install -m 644 bfd/libbfd.a %{buildroot}%{_libdir}
install -m 644 libiberty/libiberty.a %{buildroot}%{_libdir}
install -m 644 include/libiberty.h %{buildroot}%{_prefix}/include
install -m 644 opcodes/libopcodes.a %{buildroot}%{_libdir}
# Remove Windows/Novell only man pages
rm -f %{buildroot}%{_mandir}/man1/{dlltool,nlmconv,windres,windmc}*
%if %{without docs}
rm -f %{buildroot}%{_mandir}/man1/{addr2line,ar,as,c++filt,elfedit,gprof,ld,nm,objcopy,objdump,ranlib,readelf,size,strings,strip}*
rm -f %{buildroot}%{_infodir}/{as,bfd,binutils,gprof,ld}*
%endif

%if %{enable_shared}
chmod +x %{buildroot}%{_libdir}/lib*.so*
%endif

# Prevent programs from linking against libbfd and libopcodes
# dynamically, as they are changed far too often.
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.so

# Remove libtool files, which reference the .so libs
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.la

# Sanity check --enable-64-bit-bfd really works.
grep '^#define BFD_ARCH_SIZE 64$' %{buildroot}%{_prefix}/include/bfd.h
# Fix multilib conflicts of generated values by __WORDSIZE-based expressions.
%ifarch %{ix86} x86_64 ppc %{power64} s390 s390x sh3 sh4 sparc sparc64 arm
sed -i -e '/^#include "ansidecl.h"/{p;s~^.*$~#include <bits/wordsize.h>~;}' \
    -e 's/^#define BFD_DEFAULT_TARGET_SIZE \(32\|64\) *$/#define BFD_DEFAULT_TARGET_SIZE __WORDSIZE/' \
    -e 's/^#define BFD_HOST_64BIT_LONG [01] *$/#define BFD_HOST_64BIT_LONG (__WORDSIZE == 64)/' \
    -e 's/^#define BFD_HOST_64_BIT \(long \)\?long *$/#if __WORDSIZE == 32\
#define BFD_HOST_64_BIT long long\
#else\
#define BFD_HOST_64_BIT long\
#endif/' \
    -e 's/^#define BFD_HOST_U_64_BIT unsigned \(long \)\?long *$/#define BFD_HOST_U_64_BIT unsigned BFD_HOST_64_BIT/' \
    %{buildroot}%{_prefix}/include/bfd.h
%endif
touch -r bfd/bfd-in2.h %{buildroot}%{_prefix}/include/bfd.h

# Generate .so linker scripts for dependencies; imported from glibc/Makerules:

# This fragment of linker script gives the OUTPUT_FORMAT statement
# for the configuration we are building.
OUTPUT_FORMAT="\
/* Ensure this .so library will not be used by a link for a different format
   on a multi-architecture system.  */
$(gcc $CFLAGS $LDFLAGS -shared -x c /dev/null -o /dev/null -Wl,--verbose -v 2>&1 | sed -n -f "%{SOURCE2}")"

tee %{buildroot}%{_libdir}/libbfd.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

/* The libz dependency is unexpected by legacy build scripts.  */
/* The libdl dependency is for plugin support.  (BZ 889134)  */
INPUT ( %{_libdir}/libbfd.a -liberty -lz -ldl )
EOH

tee %{buildroot}%{_libdir}/libopcodes.so <<EOH
/* GNU ld script */

$OUTPUT_FORMAT

INPUT ( %{_libdir}/libopcodes.a -lbfd )
EOH

%else
# For cross-binutils we drop the documentation.
rm -rf %{buildroot}%{_infodir}
# We keep these as one can have native + cross binutils of different versions.
#rm -rf {buildroot}{_prefix}/share/locale
#rm -rf {buildroot}{_mandir}
rm -rf %{buildroot}%{_libdir}/libiberty.a
# Remove libtool files, which reference the .so libs
rm -f %{buildroot}%{_libdir}/lib{bfd,opcodes}.la
%endif

# This one comes from gcc
rm -f %{buildroot}%{_infodir}/dir
rm -rf %{buildroot}%{_prefix}/%{binutils_target}

%find_lang %{?cross}binutils
%find_lang %{?cross}opcodes
%find_lang %{?cross}bfd
%find_lang %{?cross}gas
%find_lang %{?cross}gprof
cat %{?cross}opcodes.lang >> %{?cross}binutils.lang
cat %{?cross}bfd.lang >> %{?cross}binutils.lang
cat %{?cross}gas.lang >> %{?cross}binutils.lang
cat %{?cross}gprof.lang >> %{?cross}binutils.lang

if [ -x ld/ld-new ]; then
  %find_lang %{?cross}ld
  cat %{?cross}ld.lang >> %{?cross}binutils.lang
fi
if [ -x gold/ld-new ]; then
  %find_lang %{?cross}gold
  cat %{?cross}gold.lang >> %{?cross}binutils.lang
fi

#----------------------------------------------------------------------------

%post
%if "%{build_gold}" == "both"
%__rm -f %{_bindir}/%{?cross}ld
%{_sbindir}/alternatives --install %{_bindir}/%{?cross}ld %{?cross}ld \
  %{_bindir}/%{?cross}ld.bfd %{ld_bfd_priority}
%{_sbindir}/alternatives --install %{_bindir}/%{?cross}ld %{?cross}ld \
  %{_bindir}/%{?cross}ld.gold %{ld_gold_priority}
if [ $1 = 0 ]; then
  %{_sbindir}/alternatives --auto %{?cross}ld
fi
%endif

%if %{isnative}
/sbin/ldconfig

%if %{with docs}
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/as.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/ld.info.gz
  /sbin/install-info --info-dir=%{_infodir} %{_infodir}/standards.info.gz
%endif
%endif

exit 0

#----------------------------------------------------------------------------

%preun
%if "%{build_gold}" == "both"
if [ $1 = 0 ]; then
  %{_sbindir}/alternatives --remove %{?cross}ld %{_bindir}/%{?cross}ld.bfd
  %{_sbindir}/alternatives --remove %{?cross}ld %{_bindir}/%{?cross}ld.gold
fi
%endif

%if %{isnative}
if [ $1 = 0 ]; then
  if [ -e %{_infodir}/binutils.info.gz ]
  then
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/as.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/ld.info.gz
    /sbin/install-info --quiet --delete --info-dir=%{_infodir} %{_infodir}/standards.info.gz
  fi
fi
%endif

exit 0

#----------------------------------------------------------------------------

%if %{isnative}
%postun
/sbin/ldconfig
  if [ -e %{_infodir}/binutils.info.gz ]
  then
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/as.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/binutils.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/gprof.info.gz
    /sbin/install-info --delete --info-dir=%{_infodir} %{_infodir}/ld.info.gz
    /sbin/install-info --quiet --delete --info-dir=%{_infodir} %{_infodir}/standards.info.gz
  fi
%endif

#----------------------------------------------------------------------------

%files -f %{?cross}binutils.lang
%license COPYING COPYING3 COPYING3.LIB COPYING.LIB
%doc README
%{_bindir}/%{?cross}[!l]*

%if "%{build_gold}" == "both"
%{_bindir}/%{?cross}ld.*
%ghost %{_bindir}/%{?cross}ld
%else
%{_bindir}/%{?cross}ld*
%endif

%if %{with docs}
%{_mandir}/man1/*
%if %{isnative}
%{_infodir}/as.info.gz
%{_infodir}/binutils.info.gz
%{_infodir}/gprof.info.gz
%{_infodir}/ld.info.gz
%{_infodir}/standards.info.gz
%endif
%endif

%if %{enable_shared}
%{_libdir}/lib*.so
%exclude %{_libdir}/libbfd.so
%exclude %{_libdir}/libopcodes.so
%endif

%if %{isnative}

%if %{with docs}
%{_infodir}/[^b]*info*
%{_infodir}/binutils*info*
%{_infodir}/bfd*info*
%endif

%files devel
%{_prefix}/include/*
%{_libdir}/lib*.a
%{_libdir}/libbfd.so
%{_libdir}/libopcodes.so

%endif

#----------------------------------------------------------------------------
%changelog
* Wed Jan 19 2022 Nick Clifton  <nickc@redhat.com> - 2.30-113
- When searching for plugins, do not complain if incompatible ones are found.  (#2039117)

* Thu Dec 09 2021 Nick Clifton  <nickc@redhat.com> - 2.30-112
- Make undefined unversioned dynamic symbols global rather than local.  (#2005176)

* Mon Oct 25 2021 Nick Clifton  <nickc@redhat.com> - 2.30-111
- Add ability to control the display of unicode characters.  (#2009173)

* Wed Sep 29 2021 Nick Clifton  <nickc@redhat.com> - 2.30-110
- Add support for the arch14 extensions to the s390x architecture.  (#1984819)

* Wed Sep 29 2021 Nick Clifton  <nickc@redhat.com> - 2.30-109
- Fix problems introduced by the plugin-as-needed patch.  (#2005412)

* Wed Jul 07 2021 Nick Clifton  <nickc@redhat.com> - 2.30-108
- Fix thinko in previous delta.  (#1970961)

* Wed Jun 23 2021 Nick Clifton  <nickc@redhat.com> - 2.30-107
- Fix the GOLD linker's generation of .note.gnu.property sections for x86.  (#1970961)

* Tue Jun 15 2021 Nick Clifton  <nickc@redhat.com> - 2.30-105
- Fix the handling of relocations against discarded sections.  (#1969775)

* Wed May 19 2021 Nick Clifton  <nickc@redhat.com> - 2.30-104
- Fix heap-based buffer overflow in _bfd_elf_slurp_secondary_reloc_section. (#1961526)

* Tue May 04 2021 Nick Clifton  <nickc@redhat.com> - 2.30-103
- Fix an illegal memory access when parsing a corrupt ELF file.  (#1953659)

* Mon Apr 26 2021 Nick Clifton  <nickc@redhat.com> - 2.30-102
- Bump NVR to allow rebuild against binutils-2.30-101.

* Wed Apr 14 2021 Nick Clifton  <nickc@redhat.com> - 2.30-101
- Fix excessive memory consumption in the BFD librart when parsing corrupt DWARF information.  (#1947134)

* Fri Apr 09 2021 Nick Clifton  <nickc@redhat.com> - 2.30-100
- Do not strip the static BFD library.  (For real this time).  (#1924068)
- Remove support for ARM v8.6 ISA.  (#1875912)

* Thu Mar 25 2021 Nick Clifton  <nickc@redhat.com> - 2.30-99
- Fix bug in previous patch to enable support for ARM v8.6 ISA.  (#1875912)

* Wed Mar 24 2021 Nick Clifton  <nickc@redhat.com> - 2.30-98
- Do not strip the static BFD library.  (#1924068)

* Tue Mar 23 2021 Nick Clifton  <nickc@redhat.com> - 2.30-97
- Enable support for ARM v8.6 ISA.  (#1875912)

* Fri Mar 19 2021 Nick Clifton  <nickc@redhat.com> - 2.30-96
- Fix problems involving copy relocs that refer to weak aliases.  (#1935785)

* Thu Mar 18 2021 Nick Clifton  <nickc@redhat.com> - 2.30-95
- Fix CVE involivng overwriting symlinks.  (#1920642)

* Thu Mar 18 2021 Nick Clifton  <nickc@redhat.com> - 2.30-94
- Fix LTO and weak symbols again.  (#1930988)

* Thu Feb 18 2021 Nick Clifton  <nickc@redhat.com> - 2.30-93
- Fix merging ppc64le notes.  (#1928936)

* Thu Feb 18 2021 Nick Clifton  <nickc@redhat.com> - 2.30-92
- Fix merging ppc64le notes.  (#1928936)

* Tue Feb 02 2021 Nick Clifton  <nickc@redhat.com> - 2.30-91
- Enable PEP support for all targets.  (#1920373)

* Mon Jan 11 2021 Nick Clifton  <nickc@redhat.com> - 2.30-90
- NVR bump in order to regain access to gating test results.

* Wed Dec 09 2020 Nick Clifton  <nickc@redhat.com> - 2.30-89
- Fix snafu preventing the building of the GOLD linekr.

* Wed Dec 09 2020 Nick Clifton  <nickc@redhat.com> - 2.30-88
- Fix versioning when merging common and normal symbols.  (#1904942)
- Add cross binutils support.
    
* Wed Nov 25 2020 Nick Clifton  <nickc@redhat.com> - 2.30-87
- Fix bug in patch for AArch64 GNU Property notes support.  (#1889643)

* Wed Nov 04 2020 Nick Clifton  <nickc@redhat.com> - 2.30-86
- Add support for AArch64 GNU Property notes.  (#1889643)

* Tue Nov 03 2020 Nick Clifton  <nickc@redhat.com> - 2.30-85
- Add support for the TPAUSE and UNWAIT instructions in the x86 assembler.  (#1893292)

* Mon Nov 02 2020 Nick Clifton  <nickc@redhat.com> - 2.30-84
- Fix problem in linker testsuite triggered by the as-needed update.  (#1886071)

* Fri Oct 30 2020 Nick Clifton  <nickc@redhat.com> - 2.30-83
- Fix merging attributes in the presence of multiple same-named sections.  (#1893197)

* Wed Oct 28 2020 Nick Clifton  <nickc@redhat.com> - 2.30-82
- Fix problem in linker testsuite triggered by the as-needed update.  (#1886071)

* Fri Oct 23 2020 Nick Clifton  <nickc@redhat.com> - 2.30-81
- Allow plugin syms to mark as-needed shared libs needed.  (#1886071)

* Wed Sep 16 2020 Nick Clifton  <nickc@redhat.com> - 2.30-80
- NVR Bump to allow rebuild.

* Fri Aug 21 2020 Nick Clifton  <nickc@redhat.com> - 2.30-79
- Fix x86 assembler's handling of non-8-bit displacements.  (#1869401)

* Thu Aug 20 2020 Nick Clifton  <nickc@redhat.com> - 2.30-77
- Add tests missing from PT_GNU_SEGMENT patch.  (#1870039)

* Wed Jun 24 2020 Nick Clifton  <nickc@redhat.com> - 2.30-76
- Have the s.390 assembler include alignment hints with vector instructions.  (#1850490)

* Mon Jun 15 2020 Nick Clifton  <nickc@redhat.com> - 2.30-75
- Prevent the s/390 linker from rewriting the GOT access for certain symbol types.  (#1846972)

* Tue Apr 07 2020 Nick Clifton  <nickc@redhat.com> - 2.30-74
- Stop the BFD library from issueing warning messages about allocated sections being found outside of loadable segments.  (#1630115)
- Fix linker testsuite failures for the aarch64 and s390x targets.  (#1632775, #1809101)
- Fix building the binutils with address sanitization enabled.  (#1678323)
- Add support for the PT_GNU_PROPERTY segment.  (#1721606)
- Fix an internal error in the GOLD linker.  (#1722715)
- Fix the generation of corrupt .note.gnu.property notes.  (#1723533)
- Stop objcopy's --set-section-flags option from setting the 'shared' flag on non-COFF binaries.  (#1807308)
- Fix a bug in the secondary reloc processing code.  (#1809186)

* Wed Feb 12 2020 Nick Clifton  <nickc@redhat.com> - 2.30-73
- Remove bogus assertion.  (#1801879)

* Wed Feb 12 2020 Nick Clifton  <nickc@redhat.com> - 2.30-72
- Allow the BFD library to handle the copying of files containing secondary reloc sections.  (#1801879)

* Tue Dec 03 2019 Nick Clifton  <nickc@redhat.com> - 2.30-71
- Fix a potential seg-fault in the BFD library when parsing pathalogical debug_info sections.  (#1779245)
- Fix a potential memory exhaustion in the BFD library when parsing corrupt DWARF debug information.

* Mon Dec 02 2019 Nick Clifton  <nickc@redhat.com> - 2.30-70
- Re-enable strip merging build notes.  (#1777760)

* Mon Dec 02 2019 Nick Clifton  <nickc@redhat.com> - 2.30-69
- Fix linker testsuite failures triggered by annobin update.

* Thu Nov 28 2019 Nick Clifton  <nickc@redhat.com> - 2.30-68
- Backport H.J.Lu's patch to add a workaround for the JCC Errata to the assembler.  (#1777002)

* Thu Nov 21 2019 Nick Clifton  <nickc@redhat.com> - 2.30-67
- Fix a buffer overrun in the note merging code.  (#1774507)

* Fri Nov 08 2019 Nick Clifton  <nickc@redhat.com> 2.30-66
- Fix a seg-fault in gold when linking corrupt input files.  (#1739254)

* Thu Nov 07 2019 Nick Clifton  <nickc@redhat.com> 2.30-65
- NVR bump to allow rebuild with reverted version of glibc in the buildroot.

* Wed Nov 06 2019 Nick Clifton  <nickc@redhat.com> 2.30-64
- Stop note merging with no effect from creating null filled note sections.

* Wed Nov 06 2019 Nick Clifton  <nickc@redhat.com> 2.30-63
- Stop objcopy from generating a exit failure status when merging corrupt notes.

* Fri Nov 01 2019 Nick Clifton  <nickc@redhat.com> 2.30-62
- Fix binutils testsuite failure introduced by -60 patch.  (#1767711)

* Tue Oct 29 2019 Nick Clifton  <nickc@redhat.com> 2.30-61
- Enable threading in the GOLD linker.  (#1729225)
- Add check to readelf in order to prevent an integer overflow.

* Mon Oct 28 2019 Nick Clifton  <nickc@redhat.com> 2.30-60
- Add support for SVE Vector PCS on AArch64.  (#1726637)
- Add fixes for coverity test failures.
- Improve objcopy's ability to merge GNU build attribute notes.

* Mon Oct 28 2019 Nick Clifton  <nickc@redhat.com> 2.30-59
- Stop the linker from merging groups with different settings of the SHF_EXCLUDE flag.  (#1730906)

* Fri Sep 13 2019 Nick Clifton  <nickc@redhat.com> 2.30-58
- Stop the BFD library from complaining about sections with multiple sets of relocations.  (#1749084)

* Mon May 20 2019 Nick Clifton  <nickc@redhat.com> - 2.30-57
- Fix a thinko in the new gas tests for the s390x arch13 extension.  (#1710860)

* Mon May 20 2019 Nick Clifton  <nickc@redhat.com> - 2.30-56
- Remove a spurious debugging message left in the binutils-note-merge-improvements.patch.

* Mon May 20 2019 Nick Clifton  <nickc@redhat.com> - 2.30-55
- Fix a problem when producing non-PIE binaries using the GOLD linker for AArch64.  (#1693661)

* Thu Mar 14 2019 Nick Clifton  <nickc@redhat.com> - 2.30-54
- Further enhance the support for the arch13 extensions to the s390x architecture.  (#1659437)

* Wed Mar 13 2019 Nick Clifton  <nickc@redhat.com> - 2.30-53
- Do not enable IBT when an object file contains code but no GNU Property notes.  (#1687774)

* Mon Mar 11 2019 Nick Clifton  <nickc@redhat.com> - 2.30-52
- Add support for partially relocatable GOT sections on the s390x architecture.  (#1525406)

* Mon Mar 11 2019 Nick Clifton  <nickc@redhat.com> - 2.30-51
- Add support for the arch13 extension to the s390x architecture.  (#1659437)

* Mon Mar 11 2019 Nick Clifton  <nickc@redhat.com> - 2.30-50
- Add support for disassembling NFP binaries.  (#1644391)

* Tue Oct 09 2018 Nick Clifton  <nickc@redhat.com> - 2.30-49
- Have the GOLD linker produce 8-byte aligned GNU Property notes.  (#1614908)

* Mon Oct 08 2018 Nick Clifton  <nickc@redhat.com> - 2.30-48
- Make the x86_64 linker produce IBT-enabled TLS stubs.  (PR 23000).  (#1637072)

* Tue Sep 25 2018 Nick Clifton  <nickc@redhat.com> - 2.30-47
- Fix a potential buffer overrun when parsing a corrupt ELF file.  (#1632912)

* Tue Sep 25 2018 Nick Clifton  <nickc@redhat.com> - 2.30-46
- Add a .attach_to_group pseuo-op to assembler (for use by annobin).  (#1630574)

* Thu Sep 20 2018 Nick Clifton  <nickc@redhat.com> - 2.30-45
- Stop the binutils from statically linking with libstdc++.  (#1630550)

* Thu Sep 20 2018 Nick Clifton  <nickc@redhat.com> - 2.30-44
- Include gold testsuite results in test logs.

* Wed Sep 19 2018 Nick Clifton  <nickc@redhat.com> - 2.30-43
- Add (very basic) gating tests for the binutils.  (#1625683)

* Wed Sep 12 2018 Nick Clifton  <nickc@redhat.com> - 2.30-42
- Update x86_64 linker testsuite after previous delta.  (#1624779)

* Wed Sep 05 2018 Nick Clifton  <nickc@redhat.com> - 2.30-41
- Disable the x86_64 linker's elimination of PLT entries.  (#1624779)

* Wed Sep 05 2018 Nick Clifton  <nickc@redhat.com> - 2.30-40
- Disable readelf's reporting of gaps in build notes.  (#1623556)

* Wed Sep 05 2018 Nick Clifton  <nickc@redhat.com> - 2.30-39
- Fix some more PowerPC64 linker testsuite failures.  (#1584565)

* Fri Aug 17 2018 Nick Clifton  <nickc@redhat.com> - 2.30-38
- Remove PLT eliision patch.  (#1618748)
- Restore the binutils-2.25-set-long-long.patch.

* Fri Aug 17 2018 Nick Clifton  <nickc@redhat.com> - 2.30-36
- Fix GOLDs creation of PT_NOTE segments.  (#1614908)  (#1614920)

* Mon Aug 06 2018 Nick Clifton  <nickc@redhat.com> - 2.30-35
- Improve objcopy's --merge-notes option.  (#1608390)

* Mon Jul 30 2018 Nick Clifton  <nickc@redhat.com> - 2.30-34
- Remove x86 ISA property notes with empty bits.  (#1609801)

* Mon Jul 30 2018 Florian Weimer <fweimer@redhat.com> - 2.30-33
- Rebuild with fixed binutils

* Mon Jul 30 2018 Nick Clifton  <nickc@redhat.com> - 2.30-32
- Move the .gnu.build.attributes section to after the .comment section.

* Fri Jul 27 2018 Nick Clifton  <nickc@redhat.com> - 2.30-31
- Fix a thinko in the merge patch.

* Fri Jul 27 2018 Nick Clifton  <nickc@redhat.com> - 2.30-30
- Fix a typo in the merge patch.

* Thu Jul 26 2018 Nick Clifton  <nickc@redhat.com> - 2.30-29
- Merge .gnu.build.attribute sections together.  (#1608390)

* Tue Jul 24 2018 Nick Clifton  <nickc@redhat.com> 2.30-27
- Fix the gold linker so that it can handle relocs in discardeable note sections.  (#1607054)

* Fri Jul  6 2018 Nick Clifton  <nickc@redhat.com> 2.30-26
- Fix the generation of relocations for assembler created notes.  (#1598551)

* Wed Jul  4 2018 Peter Robinson <pbrobinson@fedoraproject.org> 2.30-25
- Minor spec cleanups and fixes.

* Mon Jun 18 2018 Nick Clifton  <nickc@redhat.com> 2.30-24
- When installing both ld.bfd and ld.gold, do not reset the current alternative if upgrading.  (#1592069)

* Tue Jun 12 2018 Nick Clifton  <nickc@redhat.com> 2.30-23
- Correct warning messages about incompatible PowerPC IEEE long double settings.

* Fri Jun 01 2018 Nick Clifton  <nickc@redhat.com> 2.30-22
- Fix handling of local versioned symbols by the x86 linker.  (PR 23194)
- Fix linker testsuite failures.

* Thu May 17 2018 Nick Clifton  <nickc@redhat.com> 2.30-21
- Fix a seg-fault parsing PE format binaries.  (#1560829)

* Mon May 14 2018 Nick Clifton  <nickc@redhat.com> 2.30-20
- Have the x86 linker resolve relocations against the _end, _edata and __bss_start symbols locally.  (#1576735)
- Do not generate GNU build notes for linkonce sections.  (#1576362)

* Thu May 10 2018 Nick Clifton  <nickc@redhat.com> 2.30-19
- Fix a seg-fault running objcopy on a corrupt PE format file.  (#1574702)
- Fix a seg-fault running objcopy on a corrupt ELF format file.  (#1574705)

* Tue May 01 2018 Nick Clifton  <nickc@redhat.com> 2.30-18
- Fix a seg-fault parsing corrupt DWARF information.  (#1573360)
- Fix another seg-fault parsing corrupt DWARF information.  (#1573367)
- Fix a seg-fault copying a corrupt ELF file.  (#1551788)
- Fix a seg-fault parsing a large ELF files on a 32-bit host.  (#1539891)
- Fix a seg-fault running nm on a corrupt ELF file.  (#15343247)
- Fix a seg-fault running nm on a file containing corrupt DWARF information.  (#1551781)
- Fix another seg-fault running nm on a file containing corrupt DWARF information.  (#1551763)

* Fri Apr 27 2018 Nick Clifton  <nickc@redhat.com> 2.30-17
- Disable the automatic generation of annobin notes.  (#1572485)

* Fri Apr 27 2018 Nick Clifton  <nickc@redhat.com> 2.30-16
- Fix for PR 22887 - crashing objdump by passing it a corrupt AOUT binary.  (#1553115)
- Fix for PR 22905 - crashing objdump by passing it a corrupt DWARF file.  (#1553122)
- Fix for PR 22741 - crashing objdump by passing it a corrupt COFF file.  (#1571918)

* Thu Apr 26 2018 Nick Clifton  <nickc@redhat.com> 2.30-15
- Enhance the assembler to automatically generate annobin notes if none are present in the input.

* Thu Mar 22 2018 Nick Clifton  <nickc@redhat.com> 2.30-14
- Fix the GOLD linker's processing of protected symbols created by the LLVM plugin.  (#1559234 and PR 22868)

* Wed Mar 14 2018 Nick Clifton  <nickc@redhat.com> 2.30-13
- Do not discard debugobj files created by GCC v8 LTO wrapper.  (#1543912 and RHBZ 84847 and PR 20882)

* Fri Mar 09 2018 Nick Clifton  <nickc@redhat.com> 2.30-12
- Treat relocs against s390x IFUNC symbols in note sections as relocs against the FUNC symbol instead.
- Combined previous patches into one which covers all ifunc supporting architectures.    (#1553705)
- Retire binutils-s390-ifunc-relocs-in-notes.patch
- Retire binutils-x86_64-ifunc-relocs-in-notes.patch

* Fri Mar 09 2018 Nick Clifton  <nickc@redhat.com> 2.30-11
- Treat relocs against s390x IFUNC symbols in note sections as relocs against the FUNC symbol instead.  (#1553705)

* Wed Mar 07 2018 Nick Clifton  <nickc@redhat.com> 2.30-10
- Ignore duplicate symbols generated by GOLD.  (#1458003)

* Mon Mar 05 2018 Nick Clifton  <nickc@redhat.com> 2.30-9
- Speed up objdump.  (#1551540)

* Fri Mar 02 2018 Nick Clifton  <nickc@redhat.com> 2.30-8
- Version bump to allow rebuilding and tagging in to the buildroot.

* Tue Feb 27 2018 Nick Clifton  <nickc@redhat.com> 2.30-7
- Stop strip from replacing unknown relocs with null relocs.  (#1545386)

* Thu Feb 22 2018 Patrick Uiterwijk <patrick@puiterwijk.org> - 2.30-6
- Fix R_AARCH64 symbols (PR 22764) (#1547781)

* Thu Feb 15 2018 Nick Clifton  <nickc@redhat.com> 2.30-5
- Fix assignment of pages to segments. (PR 22758)

* Thu Feb 08 2018 Nick Clifton  <nickc@redhat.com> 2.30-4
- Inject RPM_LD_FLAGS into the build.  (#1541027)

* Thu Feb 08 2018 Nick Clifton  <nickc@redhat.com> 2.30-3
- Fix slowdown in readelf when examining files with lots of debug information.  (PR 22802)

* Thu Feb 08 2018 Nick Clifton  <nickc@redhat.com> 2.30-2
- Remove support for PowerPC speculation barrier insertion.

* Tue Feb 06 2018 Nick Clifton  <nickc@redhat.com> 2.30-1
- Rebase on 2.30

* Tue Dec 19 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-8
- Add standards.info file to documentation distributed with the binutils package.  (#1467390 and #1520899)

* Mon Dec 11 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-7
- Do not enable relro by default for the PowerPC64 architecture.  (#1523946)

* Fri Dec 08 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-6
- Stop strip from crashing when deleteing relocs in a file with annobin notes.  (#1520805)

* Wed Dec 06 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-5
- Have readelf return an exit failure status when attempting to process an empty file. (PR 22555)

* Thu Nov 16 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-4
- Prevent the PowerPC64 linker from triggering a seg-fault when discarding dynamic sections.  (#1513014)
- Prevent a seg-fault when attempting to pad a section with a NULL padding pointer.
- Do not create PLT entries for AARCH64 IFUNC symbols referenced in debug sections.
- Fix compile time warning messages.

* Wed Nov 15 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-3
- Disable PLT elision for x86/x86_64.  (#1452111 and #1333481)
- Fix the GOLD linkers generation of relocations for start and stop symbols.  (#1500898)

* Thu Sep 28 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-2
- Enable GOLD for PPC64 and s390x. (#1173780)
- Retire: binutils-2.20.51.0.10-sec-merge-emit.patch.
  (It has been redundant for a long time now...)

* Wed Sep 27 2017 Nick Clifton  <nickc@redhat.com> 2.29.1-1
- Rebase on FSF binutils 2.29.1 release.
- Retire: binutils-2.29-ppc64-plt-localentry0-disable.patch
- Retire: binutils-2.29-non-elf-orphan-skip.patch

* Thu Sep 14 2017 Nick Clifton  <nickc@redhat.com> 2.29-10
- Extend fix for PR 21884.
  (#1491023)

* Thu Sep 14 2017 Nick Clifton  <nickc@redhat.com> 2.29-8
- Import fix for PR 21884 which stops a seg-fault in the linker when changing output format to binary during a final link.
  (#1491023)

* Sun Sep 10 2017 Nick Clifton  <nickc@redhat.com> - 2.29-7
- Annotate patches with reason and lifetime expectances.
- Retire: binutils-2.24-ldforcele.patch
- Retire: binutils-2.25-set-long-long.patch
- Retire: binutils-2.25.1-cleansweep.patch
- Retire: binutils-2.26-fix-compile-warnings.patch
- Retire: binutils-2.28-ignore-gold-duplicates.patch

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.29-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Mon Jul 31 2017 Nick Clifton  <nickc@redhat.com> 2.29-5
- Update ppc64 localentry0 patch with changes made by Alan Modra to the FSF binutils sources.
  (#1475636)

* Sun Jul 30 2017 Florian Weimer <fweimer@redhat.com> - 2.29-4
- Rebuild with binutils fix for ppc64le, bootstrapping (#1475636)

* Fri Jul 28 2017 Nick Clifton  <nickc@redhat.com> 2.29-3
- Do not enable the PPC64 plt-localentry0 linker optimization by default.
  (#1475636)

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.29-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Jul 24 2017 Nick Clifton  <nickc@redhat.com> 2.29-1
- Rebase on FSF binutils 2.29.
- Retire: binutils-2.20.51.0.10-ppc64-pie.patch
- Retire: binutils-2.27-ld-buffer-overflow.patch
- Retire: binutils-2.28-libiberty-bugfixes.patch
- Retire: binutils-gnu-build-notes.patch
- Retire: binutils-2.28-gas-comp_dir.patch
- Retire: binutils-2.28-ppc-dynamic-relocs.patch
- Retire: binutils-2.28-dynamic-section-warning.patch
- Retire: binutils-2.28-aarch64-copy-relocs.patch
- Retire: binutils-2.28-DW_AT_export_symbols.patch

* Thu Jul 20 2017 Nick Clifton  <nickc@redhat.com> 2.28-14
- Remove -flto compile time option accidentally added to CFLAGS.

* Thu Jul 20 2017 Nick Clifton  <nickc@redhat.com> 2.28-13
- Add support for displaying new DWARF5 tags.
  (#1472966)

* Wed Jul 19 2017 Nick Clifton  <nickc@redhat.com> 2.28-12
- Correct snafu in previous delta that broke building s390 binaries.
  (#1472486)

* Mon Jul 17 2017 Nick Clifton  <nickc@redhat.com> 2.28-11
- Fix s390 assembler so that it remove fake local symbols from its output.
  (#1460254)

* Wed Jun 28 2017 Nick Clifton  <nickc@redhat.com> 2.28-10
- Update support for GNU Build Attribute notes to include version 2 notes.

* Thu Jun 15 2017 Nick Clifton  <nickc@redhat.com> 2.28-9
- Update patch to fix AArch64 copy reloc generation.
  (#1452170)

* Fri Jun 09 2017 Nick Clifton  <nickc@redhat.com> 2.28-8
- Ignore duplicate indirect symbols generated by the GOLD linker.
  (#1458003)

* Thu Jun 08 2017 Nick Clifton  <nickc@redhat.com> 2.28-7
- Eliminate the generation of incorrect dynamic copy relocations on AArch64.
  (#1452170)

* Mon May 15 2017 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.28-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_27_Mass_Rebuild

* Mon Mar 20 2017 Nick Clifton  <nickc@redhat.com> 2.28-5
- Update GNU BUILD NOTES patch.
- Import FSF binutils patch to fix running readelf on debug info binaries.
  (#1434050)

* Wed Mar 08 2017 Nick Clifton  <nickc@redhat.com> 2.28-4
- Update GNU BUILD NOTES patch.
- Import FSF binutils patch to fix an abort with PowerPC dynamic relocs.

* Mon Mar 06 2017 Mark Wielaard  <mjw@redhat.com> 2.28-3
- Backport patch to add support for putting name, comp_dir and
  producer strings into the .debug_str section. 
  (#1429389)

* Fri Mar 03 2017 Nick Clifton  <nickc@redhat.com> 2.28-2
- Add support for GNU BUILD NOTEs.

* Thu Mar 02 2017 Nick Clifton  <nickc@redhat.com> 2.28-1
- Rebase on FSF binutils v2.28.
- Retire: binutils-2.23.52.0.1-addr2line-dynsymtab.patch
- Retire: binutils-2.27-local-dynsym-count.patch
- Retire: binutils-2.27-monotonic-section-offsets.patch
- Retire: binutils-2.27-arm-aarch64-default-relro.patch
- Retire: binutils-2.28-gold.patch
- Retire: binutils-2.27-objdump-improvements.patch
- Retire: binutils-2.27-dwarf-parse-speedup.patch
- Retire: binutils-2.27-objdump-improvements.2.patch
- Retire: binutils-2.27-arm-binary-objects.patch
- Retire: binutils-2.27-ppc-fp-attributes.patch
- Add patch to sync libiberty with FSF GCC mainline.
  (#1428310)

* Fri Feb 17 2017 Nick Clifton  <nickc@redhat.com> 2.27-19
- Add support for PowerPC FP attributes.
  (#1422461)

* Wed Feb 15 2017 Nick Clifton  <nickc@redhat.com> 2.27-18
- Fix running the ARM port of the linker on BINARY objects.
  (#1422577)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.27-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Feb 02 2017 Stephen Gallagher  <sgallagh@redhat.com> 2.27-16
- Install COPYING[*] files using the % license macro.
  (#1418430)

* Tue Jan 31 2017 Nick Clifton  <nickc@redhat.com> 2.27-15
- Fix buffer overflows when printing translated messages.
  (#1417411)

* Mon Jan 16 2017 Nick Clifton  <nickc@redhat.com> 2.27-14
- Include the filename concerned in readelf error messages.
  (#1412348)

* Mon Jan 09 2017 Nick Clifton  <nickc@redhat.com> 2.27-13
- Another speed up for objdump when displaying source code alognside disassembly.
  (#1397113)

* Tue Nov 22 2016 Nick Clifton  <nickc@redhat.com> 2.27-12
- Speed up objdump when displaying source code alognside disassembly.
  (#1397113)

* Tue Nov 08 2016 Nick Clifton  <nickc@redhat.com> 2.27-11
- Fix objdumps disassembly of dynamic executables.
  (#1370275)

* Fri Nov 04 2016 Nick Clifton  <nickc@redhat.com> 2.27-10
- Fix GOLD for ARM and AARCH64
  (#1386126)

* Mon Sep 26 2016 Mark Pryor  <pryorm09@gmail.com> 2.27-9
- Fix invocation of /sbin/ldconfig when reinstalling binutils
  in order to prevent warnings from rpm.
  (#1379030)
  (#1379117)

* Thu Sep 22 2016 Mark Pryor  <pryorm09@gmail.com> 2.27-8
- Add i386pep emulation for all EFI capable CPU types.
  (#1376870)

* Wed Sep 21 2016 Nick Clifton  <nickc@redhat.com> 2.27-7
- Use --with-sysroot=/ for native targets.  This prevents the default
  sysroot of /usr/local/<target>/sys-root from being used, which breaks 
  locating needed shared libaries, but still allows the --sysroot
  linker command line option to be effective.
  (#1374889)
  (#1377803)
  (#1377949)

* Tue Sep 20 2016 Nick Clifton  <nickc@redhat.com> 2.27-6
- Omit building GOLD when bootstrapping.
- Add a generic build requirement on gcc.
- Move bison and m4 build requirements to be conditional upon building GOLD.
- Add --with-sysroot configure option when building native targets.
- Skip PR14918 linker test for ARM native targets.
  (#1374889)

* Fri Sep 16 2016 Nick Clifton  <nickc@redhat.com> 2.27-5
- Add support for building the rpm with "--with bootstrap" enabled.
- Retire: binutils-2.20.51.0.2-ia64-lib64.patch

* Thu Sep 01 2016 Nick Clifton  <nickc@redhat.com> 2.27-4
- Properly disable the default generation of compressed debug sections.
  (#1366182)

* Fri Aug 19 2016 Nick Clifton  <nickc@redhat.com> 2.27-3
- Put sections in a monotonically increasing order of file offset.
- Allow ARM and AArch64 targets to have relro on by default.

* Mon Aug 15 2016 Nick Clifton  <nickc@redhat.com> 2.27-2
- Fix computation of sh_info field in the header of .dynsym sections.

* Wed Aug 03 2016 Nick Clifton  <nickc@redhat.com> 2.27-1
- Rebase on FSF binutils 2.27 release.
- Retire: binutils-2.26-formatting.patch
- Retire: binutils-2.26-Bsymbolic_PIE.patch
- Retire: binutils-rh1312151.patch
- Retire: binutils-2.26-fix-GOT-offset-calculation.patch
- Retire: binutils-2.26-common-definitions.patch
- Retire: binutils-2.26-x86-PIE-relocations.patch

* Mon Jun 13 2016 Nick Clifton  <nickc@redhat.com> 2.26-23
- Enable support for GCC's LTO.
  (#1342618)

* Thu Jun 02 2016 Nick Clifton  <nickc@redhat.com> 2.26-22
- Retire the copy-osabi patch.
  (#1252066)

* Mon May 09 2016 Nick Clifton  <nickc@redhat.com> 2.26-21
- Fix another compile time warning, this time in tc-arm.c.
  (#1333695)

* Fri Apr 22 2016 Nick Clifton  <nickc@redhat.com> 2.26-20
- Housekeeping: Delete retired patches.  Renumber patches.
- Increase version number past F24 because F24 update is blocked by a version number comparison.

* Fri Mar 18 2016 Nick Clifton  <nickc@redhat.com> 2.26-16
- Import patch to fix generation of x86 relocs in PIE mode.  (PR 19827)

* Mon Mar 14 2016 Nick Clifton  <nickc@redhat.com> 2.26-15
- Import patch to have common symbols in an executable override definitions in shared objects (PR 19579)
  (#1312507)

* Mon Feb 29 2016 Nick Clifton  <nickc@redhat.com> 2.26-14
- Import patch to fix x86 GOT offset calculation in 2.26 sources (PR 19601)
  (#1312489)

* Fri Feb 26 2016 Nick Clifton  <nickc@redhat.com> 2.26-13
- Import patch to fix symbol versioning bug in 2.26 sources (PR 19698)
  (#1312151)

* Fri Feb 19 2016 Nick Clifton  <nickc@redhat.com> 2.26-12
- Import H.J.Lu's kernel LTO patch.
  (#1302071)

* Tue Feb 16 2016 poma <poma@gmail.com> 2.26-11
- Enable -Bsymbolic and -Bsymbolic-functions to PIE.  Needed by Syslinux
  (#1308296)

* Wed Feb 10 2016 Nick Clifton <nickc@redhat.com> 2.26-10
- Retire: binutils-2.23.2-aarch64-em.patch
  (#1305179)

* Tue Feb 09 2016 Nick Clifton <nickc@redhat.com> 2.26-9
- Fix indentation in bfd/elf64-s390.c, gas/config/tc-ia64.c
  and bfd/pe-mips.c to avoid compile time warnings.

* Thu Feb 04 2016 Nick Clifton <nickc@redhat.com> 2.26-8
- Fix indentation in bfd/coff-[i386|x86_64].c to avoid compile time warning.
- Suppress GOLD's dir_caches destructor.
- Suppress GOLD's Reloc_stub::Key::name function.
- Suppress unused ARM architecture variations in GAS.

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.26-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jan 27 2016 Nick Clifton <nickc@redhat.com> 2.26-4
- Drop the kernel patch entirely...
- Retire: binutils-2.25-kernel-ld-r.patch
- Retire: binutils-2.25.1-plugin-format-checking.patch

* Tue Jan 26 2016 Nick Clifton <nickc@redhat.com> 2.26-3
- Fix kernel patch for AVR targets.

* Mon Jan 25 2016 Nick Clifton <nickc@redhat.com> 2.26-2
- Fix kernel patch for PPC32 targets.

* Mon Jan 25 2016 Nick Clifton <nickc@redhat.com> 2.26-1
- Rebase on FSF binutils 2.26 release.
- Retire: binutils-2.25.1-ihex-parsing.patch
- Retire: binutils-2.25.1-dynamic_list.patch
- Retire: binutils-2.25.1-aarch64-pr18668.patch
- Retire: binutils-rh1247126.patch
  (#1271387)

* Thu Nov 05 2015 Nick Clifton <nickc@redhat.com> 2.25.1-9
- Prevent an infinite recursion when a plugin tries to claim a file in an unrecognised format.
  (#1174065)

* Wed Oct 28 2015 Nick Clifton <nickc@redhat.com> 2.25.1-8
- Enable little endian support when configuring for 64-bit PowerPC.
  (#1275709)

* Thu Sep 24 2015 Nick Clifton <nickc@redhat.com> 2.25.1-7
- Fix incorrectly generated binaries and DSOs on PPC platforms.
  (#1247126)

* Fri Sep 11 2015 Nick Clifton <nickc@redhat.com> 2.25.1-6
- Fix handling of AArch64 local GOT relocs.  (#1262091)

* Thu Sep 10 2015 Nick Clifton <nickc@redhat.com> 2.25.1-5
- Do not enable deterministic archives by default (#1195883)

* Thu Aug 06 2015 Rex Dieter <rdieter@fedoraproject.org> 2.25.1-4
- Qt linked with gold crash on startup (#1193044)

* Tue Aug 04 2015 Nick Clifton <nickc@redhat.com> - 2.25.1-3
- Fix the parsing of corrupt iHex files.
- Resovles: 1250141

* Tue Aug 04 2015 Nick Clifton <nickc@redhat.com> - 2.25.1-2
- Retire: binutils-2.25-aarch64-fPIC-error.patch
- Resovles: 1249969

* Thu Jul 23 2015 Nick Clifton <nickc@redhat.com> - 2.25.1-1
- Rebase on FSF binutils 2.25.1 release.
- Retire: binutils-2.25-x86_64-pie-relocs.patch

* Thu Jul 02 2015 Nick Clifton <nickc@redhat.com> - 2.25-12
- For AArch64 issue an error message when attempting to resolve a
  PC-relative dynamic reloc in a non-PIC object file.
- Related: 1232499

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun 10 2015 Nick Clifton <nickc@redhat.com> - 2.25-10
- Make the AArch64 GOLD port use 64K pages.
- Resolves: BZ #1225156 and BZ #1215546

* Mon Apr 27 2015 Nick Clifton <nickc@redhat.com> - 2.25-8
- Require the coreutils so that touch is available.
- Resolves: BZ #1215242

* Tue Apr 21 2015 Nick Clifton <nickc@redhat.com> - 2.25-7
- Enable building GOLD for the AArch64.
- Resolves: BZ #1203057

* Thu Mar 19 2015 Nick Clifton <nickc@redhat.com> - 2.25-6
- Remove the windmc manual page, so that it is not installed.
- Resolves: BZ #1203606

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 2.25-6
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Mon Feb 02 2015 Nick Clifton <nickc@redhat.com> - 2.25-5
- Fix scanning for object symbols in binutils-2.25-kernel-ld-r.patch
- Resolves: BZ #1149660

* Tue Jan 20 2015 Nick Clifton <nickc@redhat.com> - 2.25-4
- Import the fix for PR ld/17827 from FSF mainline.
- Resolves: BZ #1182511

* Mon Jan 12 2015 Nick Clifton <nickc@redhat.com> - 2.25-3
- Suppress building of GOLD for PPC, for now...
- Resolves: BZ #1173780

* Sat Dec 27 2014 Ralf Corsépius <corsepiu@fedoraproject.org> -  2.25-2
- Reflect configure.info/standards.info having been dropped (RHBZ#1177359).

* Wed Dec 24 2014 Nick Clifton <nickc@redhat.com> - 2.25-1
- Rebase on FSF binutils 2.25 release.
- Retire: binutils-2.24-s390-mkopc.patch
- Retire: binutils-2.24-elfnn-aarch64.patch
- Retire: binutils-2.24-DW_FORM_ref_addr.patch
- Retire: binutils-2.24-set-section-macros.patch
- Retire: binutils-2.24-fake-zlib-sections.patch
- Retire: binutils-2.24-arm-static-tls.patch
- Retire: binutils-2.24-fat-lto-objects.patch
- Retire: binutils-2.24-symbol-warning.patch
- Retire: binutils-2.24-aarch64-ld-shared-non-PIC-xfail.patch
- Retire: binutils-2.24-weak-sym-merge.patch
- Retire: binutils-2.24-indirect-chain.patch
- Retire: binutils-2.24-aarch64-fix-final_link_relocate.patch
- Retire: binutils-2.24-aarch64-fix-gotplt-offset-ifunc.patch
- Retire: binutils-2.24-aarch64-fix-static-ifunc.patch
- Retire: binutils-2.24-aarch64-fix-ie-relax.patch
- Retire: binutils-HEAD-change-ld-notice-interface.patch
- Retire: binutils-2.24-corrupt-binaries.patch
- Retire: binutils-2.24-strings-default-all.patch
- Retire: binutils-2.24-corrupt-ar.patch

* Thu Nov 13 2014 Nick Clifton <nickc@redhat.com> - 2.24-29
- Fix problems with the ar program reported in FSF PR 17533.
  Resolves: BZ #1162666, #1162655

* Fri Oct 31 2014 Nick Clifton <nickc@redhat.com> - 2.24-28
- Fix buffer overrun in ihex parser.
- Fix memory corruption in previous patch.
- Consoldiate corrupt handling patches into just one patch.
- Default strings command to using -a.

* Wed Oct 29 2014 Nick Clifton <nickc@redhat.com> - 2.24-27
- Fix memory corruption bug introduced by the previous patch.

* Tue Oct 28 2014 Nick Clifton <nickc@redhat.com> - 2.24-26
- Import patches for PR/17510 and PR/17512 to fix reading corrupt ELF binaries.
  Resolves: BZ #1157276, #1157277

* Mon Oct 27 2014 Nick Clifton <nickc@redhat.com> - 2.24-25
- Import patch from mainline to fix seg-fault when reading corrupt group headers.
  Resolves: BZ #1157276

* Fri Oct 24 2014 Nick Clifton <nickc@redhat.com> - 2.24-24
- Import patch from mainline to fix seg-fault when reading corrupt srec fields.
  Resolves: BZ #1156272

* Mon Aug 25 2014 Kyle McMartin <kmcmarti@redhat.com> - 2.24-23
- aarch64: increase common page size to 64KB
- binutils-HEAD-change-ld-notice-interface.patch: backport fix from HEAD
  that fixes LTO + ifunc when using ld.bfd instead of gold.
- binutils-2.24-aarch64-fix-gotplt-offset-ifunc.patch
  binutils-2.24-aarch64-fix-static-ifunc.patch, split elfnn-aarch64 patches
  into upstream git commits, to make it easier to figure out what's
  backported already
- binutils-2.24-aarch64-fix-ie-relax.patch: add fix for gd to ie relaxation
  when target register is >16 (pretty unlikely, but...)

* Thu Aug 21 2014 Kyle McMartin <kmcmarti@redhat.com> - 2.24-22
- bfd/elfnn-aarch64.c: use correct offsets in final_link_relocate
  Resolves: BZ #1126199

* Thu Aug 21 2014 Nick Clifton <nickc@redhat.com> - 2.24-21
- Import patch from mainline to fix indirect symbol resolution.
  Resolves: BZ #1123714

* Tue Aug 19 2014 Nick Clifton <nickc@redhat.com> - 2.24-20
- Enable deterministic archives by default.
  Resolves: BZ #1124342

* Fri Aug 15 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.24-19
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Fri Aug 15 2014 Nick Clifton <nickc@redhat.com> - 2.24-18
- Correct elf_merge_st_other arguments for weak symbols.
  Resolves: #1126436

* Tue Aug 12 2014 Jeff Law <law@redhat.com> - 2.24-17
- Enable gold for PPC.

* Tue Jun 24 2014 Kyle McMartin <kyle@redhat.com> - 2.24-16
- Backport a couple LTO testsuite fixes from HEAD.
  Default to -ffat-lto-objects for some ld tests, which was the default in
  gcc 4.8, but changed in 4.9, and resulted in some failures.
- Add STATIC_TLS flag on ARM when IE relocs are emitted in a shared
  library. Also fix up offsets in the testsuite resulting from the
  addition of the flags.
- XFail some ld tests on AArch64 to cut some of the spurious testsuite
  failures down.

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.24-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Fri May 09 2014 Nick Clifton <nickc@redhat.com> - 2.24-14
- Fix detection of little endian PPC64 binaries.  (#1095885)

* Mon Apr 28 2014 Nick Clifton <nickc@redhat.com> - 2.24-13
- Fix detection of uncompressed .debug_str sections.  (#1082370)

* Tue Apr 22 2014 Nick Clifton <nickc@redhat.com> - 2.24-12
- Fix compiling using gcc 4.9  (#1087374)

* Thu Mar 27 2014 Nick Clifton <nickc@redhat.com> - 2.24-11
- Use {version} in Source string.  Delete unused patches.

* Tue Jan 28 2014 Nick Clifton <nickc@redhat.com> - 2.24-10
- Fix decoding of abbrevs using a DW_FORM_ref_addr attribute.  (#1056797)

* Tue Dec 17 2013 Nick Clifton <nickc@redhat.com> - 2.24-9
- Import fixes on 2.24 branch that affect AArch64 IFUNC and PLT handling.

* Thu Dec 05 2013 Nick Clifton <nickc@redhat.com> - 2.24-8
- Fix building opcodes library with -Werror=format-security.  (#1037026)

* Wed Dec 04 2013 Jeff Law <law@redhat.com> - 2.24-7
- Update to official binutils 2.24 release.

* Thu Nov 21 2013 Nick Clifton <nickc@redhat.com> - 2.24-6
- Update binutils 2.24 snapshot.

* Mon Nov 11 2013 Nick Clifton <nickc@redhat.com> - 2.24-5
- Update binutils 2.24 snapshot.
- Switch to using GIT instead of CVS to access the FSF repository.
- Retire binutils-2.24-nm-dynsym.patch

* Fri Oct 25 2013 Nick Clifton <nickc@redhat.com> - 2.24-4
- Update binutils 2.24 snapshot.
- Stop NM from halting if it encounters a file with no symbols when displaying dynamic symbols in multiple files.  (#1022845)

* Fri Oct 18 2013 Nick Clifton <nickc@redhat.com> - 2.24-3
- Update binutils 2.24 snapshot.

* Fri Oct 11 2013 Nick Clifton <nickc@redhat.com> - 2.24-2
- Update binutils 2.24 snapshot.

* Fri Oct 04 2013 Nick Clifton <nickc@redhat.com> - 2.24-1
- Rebase on binutils 2.24 snapshot.
- Retire: binutils-2.23.52.0.1-64-bit-thin-archives.patch,
-         binutils-2.23.52.0.1-as-doc-texinfo-fixes.patch,
-         binutils-2.23.52.0.1-check-regular-ifunc-refs.patch,
-         binutils-2.23.2-ld-texinfo-fixes.patch,
-         binutils-2.23.2-bfd-texinfo-fixes.patch,
-         binutils-2.23.2-dwz-alt-debuginfo.patch
-         binutils-2.23.2-s390-gas-machinemode.patch
-         binutils-2.23.2-xtensa.memset.patch
-         binutils-2.23.2-s390-zEC12.patch
-         binutils-2.23.2-arm-add-float-abi-to-e_flags.patch
-         binutils-2.23.51.0.1-readelf-flush-stdout.patch

* Mon Sep 09 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-14
- Make readelf flush stdout before emitting an error or warning message.  (#1005182)

* Fri Aug 30 2013 Kyle McMartin <kyle@redhat.com> 2.23.88.0.1-13
- Add the hard-float/soft-float ABI flag as appropriate for
  ET_DYN/ET_EXEC in EABI_VER5.
- Fix last changelog entry, it was release 12, not 14.

* Wed Aug 14 2013 Nick Clifton <nickc@redhat.com> 2.23.88.0.1-12
- Add support for the s/390 zEC12 architecture to gas.  (#996395)

* Mon Aug 12 2013 Nick Clifton <nickc@redhat.com> 2.23.88.0.1-11
- Fix typos in invocations of memset in elf32-xtensa.c

* Wed Aug 07 2013 Karsten Hopp <karsten@redhat.com> 2.23.88.0.1-10
- disable -Werror on ppc64p7 for #918189

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.23.88.0.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Jul 19 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-8
- Add support for the S/390 .machinemode pseudo-op to GAS.  (#986031)

* Fri Jul 05 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-7
- Add a requirement for libstdc++-static when running the GOLD testsuite.

* Wed Jun 05 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-6
- Fix building of aarch64 targets after applying the patch for kernel ld -r modules.
- Fix building when "--with debug" is specified.

* Wed May 29 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-5
- Add support for the alternative debuging files generated by the DWZ program.  (#965255)

* Fri May 17 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-4
- Import H.J.'s patch to add support for kernel ld -r modules.
- Fix errors reported by version 5.0 of texinfo when parsing bfd documentation.

* Fri Apr 26 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-3
- Fix errors reported by version 5.0 of texinfo when parsing assembler documentation.

* Thu Apr 25 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-2
- Fix errors reported by version 5.0 of texinfo when parsing linker documentation.

* Wed Apr 24 2013 Nick Clifton <nickc@redhat.com> - 2.23.88.0.1-1
- Switch over to basing sources on the official FSF binutils releases.
- Retire binutils-2.23.52.0.1-revert-pr15149.patch.
- Update binutils-2.22.52.0.1-relro-on-by-default.patch and binutils-2.23.52.0.1-as-doc-texinfo-fixes.patch.

* Wed Apr 17 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-10
- Import patch for FSF mainline PR 15371 to fix ifunc references in shared libraries.  (#927818)

* Thu Mar 14 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-9
- Enhance opncls.c:find_separate_debug_file() to look in Fedora specific locations.
- Enhance dwarf2.c:find_line() to work with shared libraries.  (#920542)

* Wed Mar 13 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-8
- Fix addr2line to use dynamic symbols if it failed to canonicalize ordinary symbols.  (#920542)

* Wed Mar 13 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-7
- Change requirement to explicitly depend upon /usr/bin/pod2man.  (#920545)

* Wed Mar 13 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-6
- Require perl for pod2man for building man pages.  (#920545)

* Fri Mar 08 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-5
- Reverts patch for PR15149 - prevents report weak DT_NEEDED symbols.  (#918003)

* Wed Mar 06 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-4
- Enable building of GOLD for the ARM.  (#908966)

* Mon Mar 04 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-3
- Fix errors reported by version 5.0 of texinfo when parsing assembler documentaion.

* Fri Mar 01 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-2
- Fix the creation of index tables in 64-bit thin archives.  (#915411)

* Thu Feb 28 2013 Nick Clifton <nickc@redhat.com> - 2.23.52.0.1-1
- Rebase on 2.23.51.0.1 release.  (#916516)

* Fri Feb 08 2013 Nick Clifton <nickc@redhat.com> - 2.23.51.0.9-2
- Enable 64-bit BFD for aarch64.  (#908904)

* Mon Feb 04 2013 Nick Clifton <nickc@redhat.com> - 2.23.51.0.9-1
- Rebase on 2.23.51.0.9 release.  (#907089)
- Retire binutils-2.23.51.0.8-arm-whitespace.patch.

* Mon Jan 21 2013 Nick Clifton <nickc@redhat.com> - 2.23.51.0.8-4
- Allow more whitespace in ARM instructions.  (#892261)

* Tue Jan 15 2013 Patsy Franklin <pfrankli@redhat.com> - 2.23.51.0.8-3
- Add bc to BuildRequires when running the testsuite.  (#895321)

* Wed Jan 02 2013 Nick Clifton <nickc@redhat.com> - 2.23.51.0.8-2
- Add runtime link with libdl.  (#889134)

* Wed Jan 02 2013 Nick Clifton <nickc@redhat.com> - 2.23.51.0.8-1
- Rebase on 2.23.51.0.8 release.  (#890382)

* Fri Dec 21 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.7-1
- Rebase on 2.23.51.0.7 release.  (#889432)

* Tue Nov 27 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.6-1
- Rebase on 2.23.51.0.6 release.  (#880508)

* Tue Nov 13 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.5-1
- Rebase on 2.23.51.0.5 release.  (#876141)
- Retire binutils-2.23.51.0.3-arm-ldralt.patch

* Tue Oct 23 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.3-3
- Rename ARM LDRALT instruction to LDALT.  (#869025) PR/14575

* Mon Oct 15 2012 Jon Ciesla <limburgher@gmail.com> - 2.23.51.0.3-2
- Provides: bundled(libiberty)

* Tue Oct 02 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.3-1
- Rebase on 2.23.51.0.3 release.  (#858560)

* Tue Sep 11 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.2-1
- Rebase on 2.23.51.0.2 release.  (#856119)
- Retire binutils-2.23.51.0.1-gold-keep.patch and binutils-rh805974.patch.

* Tue Sep 4 2012 Jeff Law <law@redhat.com> 2.23.51.0.1-4
- Correctly handle PLTOFF relocs for s390 IFUNCs.

* Tue Aug 14 2012 Karsten Hopp <karsten@redhat.com> 2.23.51.0.1-3
- apply F17 commit cd2fda5 to honour {powerpc64} macro (#834651)

* Tue Aug 14 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.1-2
- Make GOLD honour KEEP directives in linker scripts  (#8333355)

* Wed Aug 08 2012 Nick Clifton <nickc@redhat.com> - 2.23.51.0.1-1
- Rebase on 2.23.51.0.1 release.  (#846433)
- Retire binutils-2.22.52.0.4-dwz.patch, binutils-2.22.52.0.4-ar-4Gb.patch, binutils-2.22.52.0.4-arm-plt-refcount.patch, binutils-2.22.52.0.4-s390-64bit-archive.patch.

* Thu Aug 02 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.4-8
- Make the binutils-devel package depend upon the binutils package. (#845082)

* Thu Aug 02 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.4-7
- Disable checks that config.h is included before system headers.  (#845084)

* Tue Jul 17 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.4-6
- Use 64bit indicies in archives for s390 binaries.  (#835957)

* Thu Jul 05 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.4-5
- Catch attempts to create a broken symbol index with archives > 4Gb in size.  (#835957)

* Fri Jun 29 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.4-4
- Import fix for ld/14189.  (#829311)

* Fri Jun 29 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.4-3
- Fix handling of archives > 4Gb in size by importing patch for PR binutils/14302.  (#835957)

* Tue Jun 19 2012 Jakub Jelinek <jakub@redhat.com> - 2.22.52.0.4-2
- Add minimal dwz -m support.

* Wed Jun 06 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.4-1
- Rebase on 2.22.52.0.4 release.  (#829027)

* Tue May 08 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.3-1
- Rebase on 2.22.52.0.3 release.  (#819823)

* Mon Apr 30 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.2-1
- Rebase on 2.22.52.0.2 release.  (#816514)
- Retire binutils-2.22.52.0.1-weakdef.patch, binutils-2.22.52.0.1-ld-13621.patch, binutils-rh797752.patch, binutils-2.22.52.0.1-x86_64-hidden-ifunc.patch, binutils-2.22.52.0.1-tsx.patch and binutils-2.22.52.0.1-hidden-ifunc.patch.
- Update binutils-2.22.52.0.1-reloc-on-by-default.patch.

* Fri Apr 27 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.1-12
- Include demangle.h in the devel rpm.

* Tue Apr 03 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.1-11
- Enable -zrelro by default for RHEL 7+. (#807831)

* Fri Mar 16 2012 Jakub Jelinek <jakub@redhat.com> - 2.22.52.0.1-10
- Fix up handling of hidden ifunc relocs on i?86

* Wed Mar 14 2012 Jeff Law <law@redhat.com> - 2.22.52.0.1-9
- Fix c++filt docs (2nd instance) (#797752)

* Wed Mar 07 2012 Jakub Jelinek <jakub@redhat.com> - 2.22.52.0.1-8
- Fix up handling of hidden ifunc relocs on x86_64
- Add Intel TSX support

* Tue Mar 06 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.1-7
- Enable -zrelro by default. (#621983 #807831)

* Mon Feb 27 2012 Jeff Law <law@redhat.com> - 2.22.52.0.1-6
- Fix c++filt docs (#797752)

* Wed Feb 15 2012 Mark Wielaard <mjw@redhat.com> - 2.22.52.0.1-5
- Add upstream ld/13621 'dangling global hidden symbol in symtab' patch.

* Wed Feb 08 2012 Adam Williamson <awilliam@redhat.com> - 2.22.52.0.1-4
- Actually apply the patch

* Wed Feb 08 2012 Adam Williamson <awilliam@redhat.com> - 2.22.52.0.1-3
- Add upstream weakdef.patch to fix RH #788107

* Wed Feb 01 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.1-2
- Drat - forgot to upload the new tarball.  Now done.

* Wed Feb 01 2012 Nick Clifton <nickc@redhat.com> - 2.22.52.0.1-1
- Rebase on 2.22.52 release.
- Remove build-id.patch and gold-casts.patch as they are included in the 2.22.52 sources.

* Fri Jan 13 2012 Nick Clifton <nickc@redhat.com> - 2.22-4
- Fix bug in GOLD sources parsing signed integers in command line options. 

* Fri Jan 13 2012 Nick Clifton <nickc@redhat.com> - 2.22-3
- Add casts for building gold with 4.7 version of gcc.

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.22-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov  22 2011 Nick Clifton <nickc@redhat.com> - 2.22-1
- Rebase on 2.22 release.

* Fri Sep  30 2011 Ricky Zhou <ricky@fedoraproject.org> - 2.21.53.0.2-2
- Rebuild libopcodes.a with -fPIC.

* Tue Aug  09 2011 Nick Clifton <nickc@redhat.com> - 2.21.53.0.2-1
- Rebase on 2.21.53.0.2 tarball.  Delete unneeded patches.  (BZ 728677)

* Tue Aug  02 2011 Nick Clifton <nickc@redhat.com> - 2.21.53.0.1-3
- Update libiberty demangling.  (BZ 727453)

* Wed Jul  27 2011 Nick Clifton <nickc@redhat.com> - 2.21.53.0.1-2
- Import Jakub Jelinek's patch to add support for displaying the contents of .debug_macro sections.

* Tue Jul  19 2011 Nick Clifton <nickc@redhat.com> - 2.21.53.0.1-1
- Rebase on 2.21.53.0.1 tarball.  Delete unneeded patches.  (BZ 712668)

* Fri Jun  24 2011 Nick Clifton <nickc@redhat.com> - 2.21.52.0.1-5
- Import fix for PR ld/12921.

* Fri Jun  24 2011 Nick Clifton <nickc@redhat.com> - 2.21.52.0.1-4
- Run "alternatives --auto" to restore ld symbolic link if it was manually configured.  (BZ 661247)

* Thu Jun  16 2011 Nick Clifton <nickc@redhat.com> - 2.21.52.0.1-3
- Fix seg-fault attempting to find a function name without a symbol table.  (BZ 713471)

* Fri Jun  10 2011 Nick Clifton <nickc@redhat.com> - 2.21.52.0.1-2
- Import fix for PR ld/12851 (BZ 711268)

* Thu Jun  09 2011 Nick Clifton <nickc@redhat.com> - 2.21.52.0.1-1
- Rebase on 2.21.52.0.1 tarball.  (BZ 712025)

* Tue May  17 2011 Nick Clifton <nickc@redhat.com> - 2.21.51.0.9-1
- Rebase on 2.21.51.0.9 tarball.  (BZ 703105)

* Mon May   2 2011 Peter Robinson <pbrobinson@gmail.com> - 2.21.51.0.8-3
- Add ARM to BFD checks

* Mon Apr  11 2011 Nick Clifton <nickc@redhat.com> - 2.21.51.0.8-2
- Delete plugins patch - enable plugins via configure option.

* Mon Apr  11 2011 Nick Clifton <nickc@redhat.com> - 2.21.51.0.8-1
- Rebase on 2.21.51.0.8 tarball.

* Thu Mar  17 2011 Nick Clifton <nickc@redhat.com> - 2.21.51.0.7-1
- Rebase on 2.21.51.0.7 tarball.

* Tue Mar  08 2011 Nick Clifton <nickc@redhat.com> - 2.21.51.0.6-2
- Enable gold plugins.  (BZ 682852)

* Thu Feb  10 2011 Nick Clifton <nickc@redhat.com> - 2.21.51.0.6-1
- Rebase on 2.21.51.0.6 tarball.

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.21.51.0.5-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Fri Jan  28 2011 Jakub Jelinek <jakub@redhat.com> - 2.21.51.0.5-3
- Readd --build-id fix patch.  (PR ld/12451)

* Thu Jan   6 2011 Dan Horák <dan[at]danny.cz> - 2.21.51.0.5-2
- fix build on non-gold arches like s390(x) where both ld and ld.bfd is installed

* Wed Jan   5 2011 Nick Clifton <nickc@redhat.com> - 2.21.51.0.5-1
- Rebase on 2.21.51.0.5 tarball.
- Delete redundant patches.
- Fix gold+ld configure command line option.

* Fri Nov   5 2010 Dan Horák <dan[at]danny.cz> - 2.20.51.0.12-2
- "no" is not valid option for --enable-gold

* Thu Oct  28 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.12-1
- Rebase on 2.20.51.0.12 tarball.  (BZ 582160)

* Fri Sep  10 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.11-1
- Rebase on 2.20.51.0.11 tarball.  (BZ 631771)

* Fri Aug  20 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.10-3
- Allow ^ and ! characters in linker script wildcard patterns.  (BZ 621742)

* Fri Aug  20 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.10-2
- Fix seg fault in sec_merge_emit().  (BZ 623687)

* Tue Aug  10 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.10-1
- Rebase on 2.20.51.0.10 tarball.
- Import GOLD sources from binutils mainline as of 10 Aug 2010. 

* Wed Jun  30 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.7-5
- Rename the binutils-static package to binutils-devel in line with the Fedora packaging guidelines.

* Wed Jun   9 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.7-4
- Allow GOLD linker to parse "-l<name>" directives inside INPUT statements in linker scripts. (BZ 600553)

* Tue May   4 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.7-3
- Allow unique symbols in archive maps.

* Tue Apr  20 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.7-2
- Merge binutils-devel package into binutils-static package.  (BZ 576300)

* Thu Apr   8 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.7-1
- Rebase on 2.20.51.0.7 tarball.
- Delete redundant patches:
  binutils-2.20.51.0.2-add-needed.patch,
  binutils-2.20.51.0.2-do-not-set-ifunc.patch,
  binutils-2.20.51.0.2-enable-gold.patch,
  binutils-2.20.51.0.2-gas-expr.patch,
  binutils-2.20.51.0.2-ifunc-ld-s.patch,
  binutils-2.20.51.0.2-lwp.patch,
  binutils-2.20.51.0.2-ppc-hidden-plt-relocs.patch,
  binutils-2.20.51.0.2-x86-hash-table.patch,
- Do not allow unique symbols to be bound locally.  (PR ld/11434)
- Add support for DWARF4 debug information.

* Thu Mar   4 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-17
- Do not set ELFOSABI_LINUX on binaries which just link to IFUNC using DSOs.  (BZ 568941)

* Tue Mar   2 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-16
- Copy the OSABI field in ELF headers, if set.  (BZ 568921)

* Fri Feb  12 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-15
- Create separate static and devel sub-packages.  (BZ 556040)

* Tue Feb   2 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-14
- Fix seg-fault when linking mixed x86 and x86_64 binaries.  (BZ 487472)

* Fri Jan  22 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-13
- Add a requirement for the coreutils.  (BZ 557006)

* Wed Jan  20 2010 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-12
- Fix --no-copy-dt-needed so that it will not complain about weak references.

* Fri Dec  18 2009 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-11
- Add missing part of PR 11088 patch.

* Thu Dec  17 2009 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-10
- Apply patch for PR 11088.  (BZ 544149)

* Wed Dec  9 2009 Nick Clifton <nickc@redhat.com> - 2.20.51.0.2-9
- Apply patch for PR 10856.  (BZ 544358)

* Tue Dec  1 2009 Roland McGrath <roland@redhat.com> - 2.20.51.0.2-8
- Build gold only for x86 flavors until others are tested.

* Tue Nov 24 2009 Roland McGrath <roland@redhat.com> - 2.20.51.0.2-7
- Add support for building gold.

* Mon Nov  9 2009 Jakub Jelinek <jakub@redhat.com> 2.20.51.0.2-5
- Fix up --copy-dt-needed-entries default.  (Nick Clifton)

* Mon Nov  9 2009 Jakub Jelinek <jakub@redhat.com> 2.20.51.0.2-4
- Fix ld -s with IRELATIVE relocations.  (BZ 533321, PR ld/10911)
- Add AMD Orochi LWP support, fix FMA4 support.

* Thu Nov 05 2009 Nick CLifton <nickc@redhat.com> 2.20.51.0.2-3
- Rename --add-needed to --copy-dt-needed-entries and improve error message about unresolved symbols in DT_NEEDED DSOs.

* Tue Oct 27 2009 Jan Kratochvil <jan.kratochvil@redhat.com> 2.20.51.0.2-2
- Fix rpm --excludedocs (BZ 515922).
- Fix spurious scriplet errors by `exit 0'. (BZ 517979, Nick Clifton)

* Mon Oct 12 2009 Nick Clifton <nickc@redhat.com> 2.20.51.0.2-1
- Rebase on 2.20 tarball.
- Remove redundant moxie patch.
- Remove redundant unique is global patch.
- Remove redundant cxxfilt java doc patch.

* Tue Sep 29 2009 Jan Kratochvil <jan.kratochvil@redhat.com> 2.19.51.0.14-32
- Remove spurious description of nonexistent --java switch for cxxfilt.

* Thu Aug  6 2009 Jakub Jelinek <jakub@redhat.com> 2.19.51.0.14-31
- Fix strip on objects with STB_GNU_UNIQUE symbols. (BZ 515700, PR binutils/10492)

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.19.51.0.14-30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 22 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.11-28
- Rebase sources on 2.19.51.0.14 tarball.  Gain fixes for PRs 10429 and 10433.

* Wed Jul 22 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.11-28
- Rebase sources on 2.19.51.0.13 tarball.  Remove redundant orphan section placement patch. (BZ 512937)

* Tue Jul 14 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.11-27
- Add patch to allow moxie target to build, and hence --enable-targets=all to work.

* Tue Jul 14 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.11-26
- Import orphan section placement patch from mainline.  (BZ 510384)

* Tue Jul 14 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.11-25
- Fix build-id patch to avoid memory corruption.  (BZ 501582)

* Sat Jul 11 2009 Jan Kratochvil <jan.kratochvil@redhat.com> 2.19.51.0.11-24
- Provide uuencode output of the testsuite results.

* Tue Jun 30 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.11-23
- Rebase sources on the 2.19.51.0.11 tarball.

* Mon Jun 22 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.10-22
- Rebase sources on the 2.19.51.0.10 tarball.

* Thu Jun 11 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.2-21
- Do not attempt to set execute permission on non-regular files.  (BZ 503426)

* Tue Jun  9 2009 Jakub Jelinek <jakub@redhat.com> 2.19.51.0.2-20
- Fix .cfi_* skip over >= 64KB of code.  (PR gas/10255)

* Wed May 27 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.2-19
- Import fix for binutils PR #9938.  (BZ 500295)

* Wed Apr 15 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.2-18
- Update IBM Power 7 support patch to fix tlbilx opcode.  (BZ 494718)

* Tue Mar 17 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.2-17
- Add glibc-static to BuildRequires when running the testsuite.

* Thu Mar 05 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.2-16
- Add IBM Power7 support.  (BZ 487887)

* Mon Mar 02 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.2-15
- Add IFUNC support.  (BZ 465302)

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.19.51.0.2-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Feb 23 2009 Jan Kratochvil <jan.kratochvil@redhat.com> 2.19.50.0.2-13
- Rediff the symbolic-envvar-revert patch to comply with rpm patch --fuzz=0.

* Thu Feb  5 2009 Nick Clifton <nickc@redhat.com> 2.19.51.0.2-12
- Rebase sources on 2.19.51.0.2 tarball.  Remove linkonce-r-discard and
  gcc-expect-table patches.

* Mon Feb  2 2009 Jan Kratochvil <jan.kratochvil@redhat.com> 2.19.50.0.1-11
- Fix .eh_frame_hdr build also for .gcc_except_table LSDA refs (BZ 461675).

* Fri Jan 23 2009 Nick Clifton <nickc@redhat.com> 2.19.50.0.1-10
- Only require dejagnu if the testsuites are going to be run.  (BZ 481169)

* Sat Nov 29 2008 Nick Clifton <nickc@redhat.com> 2.19.50.0.1-8
- Add build-id patch to ensure that section contents are incorporated
  into a build id.  (BZ 472152)

* Fri Nov 21 2008 Nick Clifton <nickc@redhat.com> 2.19.50.0.1
- Rebase sources on 2.19.50.0.1 tarball.  Update all patches, trimming
  those that are no longer needed.

* Thu Oct 30 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.9-7
- Fix %%{_prefix}/include/bfd.h on 32-bit hosts due the 64-bit BFD target
  support from 2.18.50.0.8-2 (BZ 468495).

* Thu Oct 30 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.9-6
- binutils-devel now requires zlib-devel (BZ 463101 comment 5).
- Fix complains on .gnu.linkonce.r relocations to their discarded
  .gnu.linkonce.t counterparts.

* Mon Sep 22 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.9-5
- Remove %%makeinstall to comply with the spu-binutils review (BZ 452211).

* Mon Sep 22 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.9-4
- Fix *.so scripts for multilib linking (BZ 463101, suggested by Jakub Jelinek).

* Sun Sep 21 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.9-3
- Provide libbfd.so and libopcodes.so for automatic dependencies (BZ 463101).
- Fix .eh_frame_hdr build on C++ files with discarded common groups (BZ 458950).
- Provide --build and --host to fix `rpmbuild --target' biarch builds.
- Include %%{binutils_target}- filename prefix for binaries for cross builds.
- Fix multilib conflict on %%{_prefix}/include/bfd.h's BFD_HOST_64BIT_LONG_LONG.

* Mon Sep 15 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.9-2
- Package review, analysed by Jon Ciesla and Patrice Dumas (BZ 225615).
 - build back in the sourcedir without problems as gasp is no longer included.
 - Fix the install-info requirement.
 - Drop the needless gzipping of the info files.
 - Provide Obsoletes versions.
 - Use the %%configure macro.

* Sat Aug 30 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.9-1
- Update to 2.18.50.0.9.
  - Drop the ppc-only spu target pre-build stage (BZ 455242).
  - Drop parsing elf64-i386 files for kdump PAE vmcore dumps (BZ 457189).
- New .spec BuildRequires zlib-devel (/-static) for compressed sections.
- Update .spec Buildroot to be more unique.

* Fri Aug  1 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.8-2
- Fix parsing elf64-i386 files for kdump PAE vmcore dumps (BZ 457189).
- Turn on 64-bit BFD support for i386, globally enable AC_SYS_LARGEFILE.
- `--with debug' builds now with --disable-shared.
- Removed a forgotten unused ld/eelf32_spu.c workaround from 2.18.50.0.8-1.

* Thu Jul 31 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.8-1
- Update to 2.18.50.0.8.
  - Drop the .clmul -> .pclmul renaming backport.
- Add %%{binutils_target} macro to support building cross-binutils.
  (David Woodhouse)
- Support `--without testsuite' to suppress the testsuite run.
- Support `--with debug' to build without optimizations.
- Refresh the patchset with fuzz 0 (for new rpmbuild).
- Enable the spu target on ppc/ppc64 (BZ 455242).

* Wed Jul 16 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.6-4
- include the `dist' tag in the Release number
- libbfd.a symbols visibility is now hidden (for #447426, suggested by Jakub)

* Wed Jul 16 2008 Jan Kratochvil <jan.kratochvil@redhat.com> 2.18.50.0.6-3
- rebuild libbfd.a with -fPIC for inclusion into shared libraries (#447426)

* Tue Apr  8 2008 Jakub Jelinek <jakub@redhat.com> 2.18.50.0.6-2
- backport .clmul -> .pclmul renaming

* Fri Apr  4 2008 Jakub Jelinek <jakub@redhat.com> 2.18.50.0.6-1
- update to 2.18.50.0.6
  - Intel AES, CLMUL, AVX/FMA support

* Mon Mar  3 2008 Jakub Jelinek <jakub@redhat.com> 2.18.50.0.4-2
- revert aranges optimization (Alan Modra, BZ#5303, BZ#5755)
- fix ld-shared testcase for GCC 4.3 (H.J. Lu)

* Fri Feb 29 2008 Jakub Jelinek <jakub@redhat.com> 2.18.50.0.4-1
- update to 2.18.50.0.4

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> 2.18.50.0.3-2
- Autorebuild for GCC 4.3

* Wed Dec 12 2007 Jakub Jelinek <jakub@redhat.com> 2.18.50.0.3-1
- update to 2.18.50.0.3
  - fix build with recent makeinfo (#415271)

* Thu Aug 16 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.18-1
- update to 2.17.50.0.18
  - GPLv3+
  - preserve .note.gnu.build-id in objcopy --only-keep-debug (#251935)
  - fix sparc64/alpha broken by --build-id patch (#252936)
- update License tag
- fix ld crash with --build-id and non-ELF output format (Alan Modra, BZ#4923)

* Tue Jul 31 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.17-7
- fix ppc32 secure PLT detection (Alan Modra)

* Wed Jul 25 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.17-6
- rebuilt to make sure even libbfd.so and libopcodes.so aren't
  broken by #249435

* Tue Jul 24 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.17-5
- add .note.gnu.build-id into default linker script (#249435)

* Tue Jul 24 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.17-4
- don't kill the %%{_gnu} part of target name on arm
  (Lennert Buytenhek, #243516)
- create just one PT_NOTE segment header for all consecutive SHT_NOTE
  sections

* Wed Jul 18 2007 Roland McGrath <roland@redhat.com> 2.17.50.0.17-3
- fix for ld --build-id

* Sun Jul 15 2007 Roland McGrath <roland@redhat.com> 2.17.50.0.17-2
- ld --build-id support

* Wed Jun 27 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.17-1
- update to 2.17.50.0.17

* Tue Jun 12 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.16-1
- update to 2.17.50.0.16

* Sat Apr 14 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.12-4
- fix linking non-ELF input objects into ELF output (#235747)

* Wed Mar 14 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.12-3
- don't require matching ELF_OSABI for target vecs with ELFOSABI_NONE,
  only prefer specific osabi target vecs over the generic ones
  (H.J.Lu, #230964, BZ#3826)
- build libbfd.so and libopcodes.so with -Bsymbolic-functions

* Fri Mar  2 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.12-2
- ignore install-info errors from scriptlets (#223678)

* Thu Mar  1 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.12-1
- update to 2.17.50.0.12
- revert the misdesigned LD_SYMBOLIC{,_FUNCTIONS} env var support,
  only support -Bsymbolic/-Bsymbolic-functions/--dynamic-list*

* Mon Jan  8 2007 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.9-1
- update to 2.17.50.0.9
- fix tekhex reader

* Sat Dec 23 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.8-2
- fix --as-needed on ppc64 (#219629)

* Sun Dec  3 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.8-1
- update to 2.17.50.0.8
- initialize frch_cfi_data (BZ#3607)

* Fri Dec  1 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.7-1
- update to 2.17.50.0.7
  - .cfi_personality and .cfi_lsda directives, per subsection .cfi_*
    directives, better .eh_frame CIE merging

* Thu Nov  9 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.6-3
- fix popcnt instruction assembly and disassembly on amd64 (#214767)

* Mon Oct 23 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.6-2
- update to 2.17.50.0.6
  - fix for section relative linker script defined symbols in
    empty sections (#207598, BZ#3267)
  - fix handling of DW_CFA_set_loc in .eh_frame optimizations
  - fix R_PPC_{PLT,GOT{,_TLSGD,_TLSLD,_TPREL,_DTPREL}}16_HA relocation
    handling with weak undefined symbols (Alan Modra, #211094)

* Tue Sep 12 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.3-6
- fix multilib conflict in %%{_prefix}/include/bfd.h

* Tue Sep 12 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.3-5
- fix efi-app-ia64 magic number (#206002, BZ#3171)

* Tue Sep  5 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.3-4
- link libopcodes*.so against libbfd*.so (#202327)
- split *.a and header files into binutils-devel

* Fri Aug 18 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.3-3
- on ppc and ppc64 increase default -z commonpagesize to 64K (#203001)

* Fri Jul 28 2006 Alexandre Oliva <aoliva@redhat.com> 2.17.50.0.3-2
- do not infer x86 arch implicitly based on instruction in the input
  (#200330)

* Mon Jul 17 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.3-1
- update to 2.17.50.0.3

* Fri Jul 14 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.2-8
- add support for new AMDFAM10 instructions (#198281, IT#97662)
- add -march=/-mtune= gas support on x86/x86-64
- x86/x86-64 nop insn improvements
- fix DT_GNU_HASH shift count value computation

* Tue Jul 11 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.2-7
- add DT_GNU_HASH support (--hash-style=gnu and --hash-style=both
  ld options)

* Thu Jun 29 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.2-4
- fix i?86 TLS GD->IE transition in executables (#196157, BZ#2513)

* Mon Jun 19 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.2-3
- fix two places in ld that misbehaved with MALLOC_PERTURB_=N
- fix .tls_common handling in relocatable linking

* Mon Jun  5 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.2-2
- fix --as-needed (Alan Modra, #193689, BZ#2721)

* Thu Jun  1 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.2-1
- update to 2.17.50.0.2
- update from CVS to 20060601
- speed up the ELF linker by caching the result of kept section check
  (H.J. Lu)

* Tue May  9 2006 Jakub Jelinek <jakub@redhat.com> 2.17.50.0.1-1
- update to 2.17.50.0.1

* Fri Mar 31 2006 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.6-6
- fix ld error message formatting, so that collect2 parser can
  parse it again for g++ -frepo (#187142)

* Thu Mar  9 2006 Alexandre Oliva <aoliva@redhat.com> 2.16.91.0.6-4
- fix relaxation of TLS GD to LE on PPC (#184590)

* Fri Mar  3 2006 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.6-3
- support DW_CFA_val_{offset,offset_sf,expression} in readelf/objdump

* Tue Feb 28 2006 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.6-2
- add MNI support on i?86/x86_64 (#183080)
- support S signal frame augmentation flag in .eh_frame,
  add .cfi_signal_frame support (#175951, PR other/26208, BZ#300)

* Tue Feb 14 2006 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.6-1
- update to 2.16.91.0.6
  - fix ppc64 --gc-sections
  - disassembler fixes for x86_64 cr/debug regs
  - fix linker search order for DT_NEEDED libs

* Mon Jan 02 2006 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.5-1
- update to 2.16.91.0.5
- don't error about .toc1 references to discarded sectiosn on ppc64
  (#175944)

* Wed Dec 14 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.3-2
- put .gnu.linkonce.d.rel.ro.* sections into relro region

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Nov 11 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.3-1
- update to 2.16.91.0.3
- add .weakref support (Alexandre Oliva, #115157, #165728)

* Thu Aug 18 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.2-4
- install-info also configure.info
- update standards.texi from gnulib (#165530)

* Tue Aug 16 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.2-3
- update to 20050816 CVS
- better fix for ld-cdtest
- fix symbol version script parsing

* Fri Jul 29 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.2-2
- don't complain about relocs to discarded sections in ppc32
  .got2 sections (Alan Modra, PR target/17828)

* Fri Jul 22 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.2-1
- update to 2.16.91.0.2

* Thu Jul 21 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.1-3
- fix buffer overflow in readelf ia64 unwind printing code
- use vsnprintf rather than vsprintf in gas diagnostics (Tavis Ormandy)
- fix ld-cdtest when CFLAGS contains -fexceptions

* Wed Jul 20 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.1-2
- update to 20050720 CVS

* Mon Jul 11 2005 Jakub Jelinek <jakub@redhat.com> 2.16.91.0.1-1
- update to 2.16.91.0.1 plus 20050708 CVS

* Wed Jun 15 2005 Jakub Jelinek <jakub@redhat.com> 2.16.90.0.3-1
- update to 2.16.90.0.3
- update to 20050615 CVS
  - ppc32 secure PLT support (Alan Modra)
- further bfd/readelf robustification

* Sat Jun 11 2005 Jakub Jelinek <jakub@redhat.com> 2.15.94.0.2.2-4
- further bfd robustification (CAN-2005-1704, #158680)

* Fri Jun 10 2005 Jakub Jelinek <jakub@redhat.com> 2.15.94.0.2.2-3
- further objdump and readelf robustification (CAN-2005-1704, #158680)

* Wed May 25 2005 Jakub Jelinek <jakub@redhat.com> 2.15.94.0.2.2-2
- bfd and readelf robustification (CAN-2005-1704, #158680)

* Tue Mar 29 2005 Jakub Jelinek <jakub@redhat.com> 2.15.94.0.2.2-1
- update to 2.15.94.0.2.2
- speed up walk_wild_section (Robert O'Callahan)

* Mon Mar  7 2005 Jakub Jelinek <jakub@redhat.com> 2.15.94.0.2-4
- rebuilt with GCC 4

* Mon Feb 28 2005 Jakub Jelinek <jakub@redhat.com> 2.15.94.0.2-3
- fix buffer overflows in readelf (#149506)
- move c++filt to binutils from gcc-c++, conflict with gcc-c++ < 4.0 (#86333)

* Thu Feb 10 2005 Jakub Jelinek <jakub@redhat.com> 2.15.94.0.2-1
- update to 2.15.94.0.2
- fix .note.GNU-stack/PT_GNU_STACK computation in linker on ppc64 (#147296)
- fix stripping of binaries/libraries that have empty sections right before
  .dynamic section (with the same starting address; #144038)
- handle AS_NEEDED (...) in linker script INPUT/GROUP

* Tue Dec 14 2004 Jakub Jelinek <jakub@redhat.com> 2.15.92.0.2-11
- fix a longstanding -z relro bug

* Mon Dec 13 2004 Jakub Jelinek <jakub@redhat.com> 2.15.92.0.2-10
- avoid unnecessary gap with -z relro showing on i686 libc.so
- ppc64 --emit-relocs fix (Alan Modra)
- don't crash if STT_SECTION symbol has incorrect st_shndx (e.g. SHN_ABS,
  as created by nasm; #142181)
- don't try to make absptr LSDAs relative if they don't have relocations
  against them (Alan Modra, #141162)

* Wed Oct 27 2004 Jakub Jelinek <jakub@redhat.com> 2.15.92.0.2-5.EL4
- fix ar xo (#104344)

* Wed Oct 20 2004 Jakub Jelinek <jakub@redhat.com> 2.15.92.0.2-5
- fix --just-symbols on ppc64 (Alan Modra, #135498)

* Fri Oct 15 2004 Jakub Jelinek <jakub@redhat.com> 2.15.92.0.2-4
- fix code detecting matching linkonce and single member comdat
  group sections (#133078)

* Mon Oct 11 2004 Jakub Jelinek <jakub@redhat.com> 2.15.92.0.2-3
- revert Sep 09 change to make ppc L second argument e.g. for tlbie
  non-optional
- fix stripping of prelinked binaries and libraries (#133734)
- allow strings(1) on 32-bit arches to be used again with > 2GB
  files (#133555)

* Mon Oct  4 2004 Jakub Jelinek <jakub@redhat.com> 2.15.92.0.2-2
- update to 2.15.92.0.2
- change ld's ld.so.conf parser to match ldconfig's (#129340)

* Mon Sep 20 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-9
- avoid almost 1MB (sparse) gaps in the middle of -z relro
  libraries on x86-64 (Andreas Schwab)
- fix -z relro to make sure end of PT_GNU_RELRO segment is always
  COMMONPAGESIZE aligned

* Wed Aug 18 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-8
- fix linker segfaults on input objects with SHF_LINK_ORDER with
  incorrect sh_link (H.J.Lu, Nick Clifton, #130198, BZ #290)

* Wed Aug 18 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-7
- resolve all undefined ppc64 .* syms to the function bodies through
  .opd, not just those used in brach instructions (Alan Modra)

* Tue Aug 17 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-6
- fix ppc64 ld --dotsyms (Alan Modra)

* Tue Aug 17 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-5
- various ppc64 make check fixes when using non-dot-syms gcc (Alan Modra)
- fix --gc-sections
- on ia64 create empty .gnu.linkonce.ia64unw*.* sections for
  .gnu.linkonce.t.* function doesn't need unwind info

* Mon Aug 16 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-4
- kill ppc64 dot symbols (Alan Modra)
- objdump -d support for objects without dot symbols
- support for overlapping ppc64 .opd entries

* Mon Aug 9 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-3
- fix a newly introduced linker crash on x86-64

* Sun Aug 8 2004 Alan Cox <alan@redhat.com> 2.15.91.0.2-2
- BuildRequire bison and macroise buildroot - from Steve Grubb

* Fri Jul 30 2004 Jakub Jelinek <jakub@redhat.com> 2.15.91.0.2-1
- update to 2.15.91.0.2
- BuildRequire flex (#117763)

* Wed May 19 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.3-7
- use lib64 instead of lib directories on ia64 if %%{_lib} is
  set to lib64 by rpm

* Sat May 15 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.3-6
- fix a bug introduced in the ++/-- rejection patch
  from 2.15.90.0.3 (Alan Modra)

* Tue May  4 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.3-5
- fix s390{,x} .{,b,p2}align handling
- ppc/ppc64 testsuite fix

* Mon May  3 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.3-4
- -z relro ppc/ppc64/ia64 fixes
- change x86-64 .plt symbol st_size handling to match ia32
- prettify objdump -d output

* Tue Apr 20 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.3-3
- several SPARC fixes

* Sun Apr 18 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.3-2
- yet another fix for .tbss handling

* Fri Apr 16 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.3-1
- update to 2.15.90.0.3

* Fri Mar 26 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.1.1-2
- update to 20040326 CVS
  - fix ppc64 weak .opd symbol handling (Alan Modra, #119086)
- fix .tbss handling bug introduced

* Fri Mar 26 2004 Jakub Jelinek <jakub@redhat.com> 2.15.90.0.1.1-1
- update to 2.15.90.0.1.1

* Sat Feb 21 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.8-8
- with -z now without --enable-new-dtags create DT_BIND_NOW
  dynamic entry in addition to DT_FLAGS_1 with DF_1_NOW bit set

* Fri Feb 20 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.8-7
- fix -pie on ppc32

* Fri Feb 20 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.8-6
- clear .plt sh_entsize on sparc32
- put whole .got into relro area with -z now -z relro

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jan 22 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.8-4
- fix -pie on IA64

* Mon Jan 19 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.8-3
- fix testcases on s390 and s390x

* Fri Jan 16 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.8-2
- fix testcases on AMD64
- fix .got's sh_entsize on IA32/AMD64
- set COMMONPAGESIZE on s390/s390x
- set COMMONPAGESIZE on ppc32 (Alan Modra)

* Fri Jan 16 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.8-1
- update to 2.14.90.0.8

* Tue Jan 13 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.7-4
- fix -z relro on 64-bit arches

* Mon Jan 12 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.7-3
- fix some bugs in -z relro support

* Fri Jan  9 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.7-2
- -z relro support, reordering of RW sections

* Fri Jan  9 2004 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.7-1
- update to 2.14.90.0.7

* Mon Nov 24 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.6-4
- fix assembly parsing of foo=(.-bar)/4 (Alan Modra)
- fix IA-64 assembly parsing of (p7) hint @pause

* Tue Sep 30 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.6-3
- don't abort on some linker warnings/errors on IA-64

* Sat Sep 20 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.6-2
- fix up merge2.s to use .p2align instead of .align

* Sat Sep 20 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.6-1
- update to 2.14.90.0.6
- speed up string merging (Lars Knoll, Michael Matz, Alan Modra)
- speed up IA-64 local symbol handling during linking

* Fri Sep  5 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.5-7
- avoid ld -s segfaults introduced in 2.14.90.0.5-5 (Dmitry V. Levin,
  #103180)

* Fri Aug 29 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.5-6
- build old demangler into libiberty.a (#102268)
- SPARC .cfi* support

* Tue Aug  5 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.5-5
- fix orphan section placement

* Tue Jul 29 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.5-4
- fix ppc64 elfvsb linker tests
- some more 64-bit cleanliness fixes, give ppc64 fdesc symbols
  type and size (Alan Modra)

* Tue Jul 29 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.5-3
- fix 64-bit unclean code in ppc-opc.c

* Mon Jul 28 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.5-2
- fix 64-bit unclean code in tc-ppc.c

* Mon Jul 28 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.5-1
- update to 2.14.90.0.5
- fix ld -r on ppc64 (Alan Modra)

* Fri Jul 18 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-23
- rebuilt

* Thu Jul 17 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-22
- fix elfNN_ia64_dynamic_symbol_p (Richard Henderson, #86661)
- don't access memory beyond what was allocated in readelf
  (Richard Henderson)

* Thu Jul 10 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-21
- add .cfi_* support on ppc{,64} and s390{,x}

* Tue Jul  8 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-20
- remove lib{bfd,opcodes}.la (#98190)

* Mon Jul  7 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-19
- fix -pie support on amd64, s390, s390x and ppc64
- issue relocation overflow errors for s390/s390x -fpic code when
  accessing .got slots above 4096 bytes from .got start

* Thu Jul  3 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-18
- rebuilt

* Thu Jul  3 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-17
- fix ia64 -pie support
- require no undefined non-weak symbols in PIEs like required for normal
  binaries

* Wed Jul  2 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-16
- fix readelf -d on IA-64
- build libiberty.a with -fPIC, so that it can be lined into shared
  libraries

* Wed Jun 25 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-15
- rebuilt

* Wed Jun 25 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-14
- added support for Intel Prescott instructions
- fix hint@pause for ia64
- add workaround for LTP sillyness (#97934)

* Wed Jun 18 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-13
- update CFI stuff to 2003-06-18
- make sure .eh_frame is aligned to 8 bytes on 64-bit arches,
  remove padding within one .eh_frame section

* Tue Jun 17 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-12
- rebuilt

* Tue Jun 17 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-11
- one more fix for the same patch

* Tue Jun 17 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-10
- fix previous patch

* Mon Jun 16 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-9
- ensure R_PPC64_{RELATIVE,ADDR64} have *r_offset == r_addend
  and the other relocs have *r_offset == 0

* Tue Jun 10 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-8
- remove some unnecessary provides in ppc64 linker script
  which were causing e.g. empty .ctors/.dtors section creation

* Fri Jun  6 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-7
- some CFI updates/fixes
- don't create dynamic relocations against symbols defined in PIE
  exported from its .dynsym

* Wed Jun  4 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-6
- update gas to 20030604
- PT_GNU_STACK support

* Mon Jun  2 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-5
- buildrequire gettext (#91838)

* Sat May 31 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-4
- fix shared libraries with >= 8192 .plt slots on ppc32

* Thu May 29 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-3
- rebuilt

* Thu May 29 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-2
- rename ld --dynamic option to --pic-executable or --pie
- fix ld --help output
- document --pie/--pic-executable in ld.info and ld.1

* Wed May 28 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.4-1
- update to 2.14.90.0.4-1
- gas CFI updates (Richard Henderson)
- dynamic executables (Ulrich Drepper)

* Tue May 20 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.2-2
- fix ELF visibility handling
- tidy plt entries on IA-32, ppc and ppc64

* Mon May 19 2003 Jakub Jelinek <jakub@redhat.com> 2.14.90.0.2-1
- update to 2.14.90.0.2-1

* Tue May 13 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-8
- fix bfd_elf_hash on 64-bit arches (Andrew Haley)

* Wed Apr 30 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-7
- rebuilt

* Mon Apr 14 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-6
- optimize DW_CFA_advance_loc4 in gas even if there is 'z' augmentation
  with size 0 in FDE

* Fri Apr 11 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-5
- fix SPARC build

* Thu Apr  3 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-4
- fix ppc32 plt reference counting
- don't include %%{_prefix}/%%{_lib}/debug in the non-debuginfo package
  (#87729)

* Mon Mar 31 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-3
- make elf64ppc target native extra on ppc and elf32ppc native extra
  on ppc64.

* Fri Mar 28 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-2
- fix TLS on IA-64 with ld relaxation

* Sat Mar 22 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.20-1
- update to 2.13.90.0.20

* Mon Feb 24 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-9
- rebuilt

* Mon Feb 24 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-8
- don't strip binaries in %%install, so that there is non-empty
  debuginfo

* Mon Feb 24 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-7
- don't optimize .eh_frame during ld -r

* Thu Feb 13 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-6
- don't clear elf_link_hash_flags in the .symver patch
- only use TC_FORCE_RELOCATION in s390's TC_FORCE_RELOCATION_SUB_SAME
  (Alan Modra)

* Mon Feb 10 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-5
- fix the previous .symver change
- remove libbfd.so and libopcodes.so symlinks, so that other packages
  link statically, not dynamically against libbfd and libopcodes
  whose ABI is everything but stable

* Mon Feb 10 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-4
- do .symver x, x@FOO handling earlier
- support .file and .loc on s390*

* Mon Feb 10 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-3
- handle .symver x, x@FOO in ld such that relocs against x become
  dynamic relocations against x@FOO (#83325)
- two PPC64 TLS patches (Alan Modra)

* Sun Feb 09 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-2
- fix SEARCH_DIR on x86_64/s390x
- fix Alpha --relax
- create DT_RELA{,SZ,ENT} on s390 even if there is just .rela.plt
  and no .rela.dyn section
- support IA-32 on IA-64 (#83752)
- .eh_frame_hdr fix (Andreas Schwab)

* Thu Feb 06 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.18-1
- update to 2.13.90.0.18 + 20030121->20030206 CVS diff

* Tue Feb 04 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-8
- alpha TLS fixes
- use .debug_line directory table to make the section tiny bit smaller
- libtool fix from Jens Petersen

* Sun Feb 02 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-7
- sparc32 TLS

* Fri Jan 24 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-6
- s390{,x} TLS and two other mainframe patches

* Fri Jan 17 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-5
- fix IA-64 TLS IE in shared libs
- .{preinit,init,fini}_array compat hack from Alexandre Oliva

* Thu Jan 16 2003 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-4
- IA-64 TLS fixes
- fix .plt sh_entsize on Alpha
- build with %%_smp_mflags

* Sat Nov 30 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-3
- fix strip on TLS binaries and libraries

* Fri Nov 29 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-2
- fix IA-64 ld bootstrap

* Thu Nov 28 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.16-1
- update to 2.13.90.0.16
- STT_TLS SHN_UNDEF fix

* Wed Nov 27 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.10-4
- pad .rodata.cstNN sections at the end if they aren't sized to multiple
  of sh_entsize
- temporary patch to make .eh_frame and .gcc_except_table sections
  readonly if possible (should be removed when AUTO_PLACE is implemented)
- fix .PPC.EMB.apuinfo section flags

* Wed Oct 23 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.10-3
- fix names and content of alpha non-alloced .rela.* sections (#76583)
- delete unpackaged files from the buildroot

* Tue Oct 15 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.10-2
- enable s390x resp. s390 emulation in linker too

* Mon Oct 14 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.10-1
- update to 2.13.90.0.10
- add a bi-arch patch for sparc/s390/x86_64
- add --enable-64-bit-bfd on sparc, s390 and ppc

* Thu Oct 10 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.4-3
- fix combreloc testcase

* Thu Oct 10 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.4-2
- fix orphan .rel and .rela section placement with -z combreloc (Alan Modra)
- skip incompatible linker scripts when searching for libraries

* Tue Oct  1 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.4-1
- update to 2.13.90.0.4
- x86-64 TLS support
- some IA-32 TLS fixes
- some backported patches from trunk
- include opcodes, ld, gas and bfd l10n too

* Thu Sep 19 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.2-3
- allow addends for IA-32 TLS @tpoff, @ntpoff and @dtpoff
- clear memory at *r_offset of dynamic relocs on PPC
- avoid ld crash if accessing non-local symbols through LE relocs
- new IA-32 TLS relocs, bugfixes and testcases
- use brl insn on IA-64 (Richard Henderson)
- fix R_IA64_PCREL21{M,F} handling (Richard Henderson)
- build in separate builddir, so that gasp tests don't fail
- include localization

* Thu Aug  8 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.2-2
- fix R_386_TPOFF32 addends (#70824)

* Sat Aug  3 2002 Jakub Jelinek <jakub@redhat.com> 2.13.90.0.2-1
- update to 2.13.90.0.2
  - fix ld TLS assertion failure (#70084)
  - fix readelf --debug-dump= handling to match man page and --help
    (#68997)
- fix _GLOBAL_OFFSET_TABLE gas handling (#70241)

* Wed Jul 24 2002 Jakub Jelinek <jakub@redhat.com> 2.12.90.0.15-1
- update to 2.12.90.0.15
- TLS .tbss fix
- don't use rpm %%configure macro, it is broken too often (#69366)

* Thu May 30 2002 Jakub Jelinek <jakub@redhat.com> 2.12.90.0.9-1
- update to 2.12.90.0.9
  - TLS support
- remove gasp.info from %%post/%%preun (#65400)

* Mon Apr 29 2002 Jakub Jelinek <jakub@redhat.com> 2.12.90.0.7-1
- update to 2.12.90.0.7
- run make check

* Mon Apr 29 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-12
- fix .hidden handling on SPARC (Richard Henderson)
- don't crash when linking -shared non-pic code with SHF_MERGE
- fix .eh_frame_hdr for DW_EH_PE_aligned
- correctly adjust DW_EH_PE_pcrel encoded personalities in CIEs

* Fri Apr  5 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-11
- don't emit dynamic R_SPARC_DISP* relocs against STV_HIDDEN symbols
  into shared libraries

* Thu Mar 21 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-10
- don't merge IA-64 unwind info sections together during ld -r

* Mon Mar 11 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-9
- fix DATA_SEGMENT_ALIGN on ia64/alpha/sparc/sparc64

* Fri Mar  8 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-8
- don't crash on SHN_UNDEF local dynsyms (Andrew MacLeod)

* Thu Mar  7 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-7
- fix bfd configury bug (Alan Modra)

* Tue Mar  5 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-6
- don't copy visibility when equating symbols
- fix alpha .text/.data with .previous directive bug

* Tue Mar  5 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-5
- fix SHF_MERGE crash with --gc-sections (#60369)
- C++ symbol versioning patch

* Fri Feb 22 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-4
- add DW_EH_PE_absptr -> DW_EH_PE_pcrel optimization for shared libs,
  if DW_EH_PE_absptr cannot be converted that way, don't build the
  .eh_frame_hdr search table

* Fri Feb 15 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-3
- fix ld -N broken by last patch

* Tue Feb 12 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-2
- trade one saved runtime page for data segment (=almost always not shared)
  for up to one page of disk space where possible

* Fri Feb  8 2002 Jakub Jelinek <jakub@redhat.com> 2.11.93.0.2-1
- update to 2.11.93.0.2
- use %%{ix86} instead of i386 for -z combreloc default (#59086)

* Thu Jan 31 2002 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-10
- don't create SHN_UNDEF STB_WEAK symbols unless there are any relocations
  against them

* Wed Jan 30 2002 Bill Nottingham <notting@redhat.com> 2.11.92.0.12-9.1
- rebuild (fix ia64 miscompilation)

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Dec 28 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-8
- two further .eh_frame patch fixes

* Wed Dec 19 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-7
- as ld is currently not able to shrink input sections to zero size
  during discard_info, build a fake minimal CIE in that case
- update elf-strtab patch to what was commited

* Mon Dec 17 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-6
- one more .eh_frame patch fix
- fix alpha .eh_frame handling
- optimize elf-strtab finalize

* Sat Dec 15 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-5
- yet another fix for the .eh_frame patch

* Fri Dec 14 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-4
- Alan Modra's patch to avoid crash if there is no dynobj

* Thu Dec 13 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-3
- H.J.'s patch to avoid crash if input files are not ELF
- don't crash if a SHF_MERGE for some reason could not be merged
- fix objcopy/strip to preserve SHF_MERGE sh_entsize
- optimize .eh_frame sections, add PT_GNU_EH_FRAME support
- support anonymous version tags in version script

* Tue Nov 27 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-2
- fix IA-64 SHF_MERGE handling

* Tue Nov 27 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.12-1
- update to 2.11.92.0.12
  - optimize .dynstr and .shstrtab sections (#55524)
  - fix ld.1 glitch (#55459)
- turn relocs against SHF_MERGE local symbols with zero addend
  into STT_SECTION + addend
- remove man pages for programs not included (nlmconv, windres, dlltool;
  #55456, #55461)
- add BuildRequires for texinfo

* Thu Oct 25 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.7-2
- duh, fix strings on bfd objects (#55084)

* Sat Oct 20 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.7-1
- update to 2.11.92.0.7
- remove .rel{,a}.dyn from output if it is empty

* Thu Oct 11 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.5-2
- fix strings patch
- use getc_unlocked in strings to speed it up by 50% on large files

* Wed Oct 10 2001 Jakub Jelinek <jakub@redhat.com> 2.11.92.0.5-1
- update to 2.11.92.0.5
  - binutils localization (#45148)
  - fix typo in REPORT_BUGS_TO (#54325)
- support files bigger than 2GB in strings (#54406)

* Wed Sep 26 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-12
- on IA-64, don't mix R_IA64_IPLTLSB relocs with non-PLT relocs in
  .rela.dyn section.

* Tue Sep 25 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-11
- add iplt support for IA-64 (Richard Henderson)
- switch to new section flags for SHF_MERGE and SHF_STRINGS, put
  in compatibility code
- "s" section flag for small data sections on IA-64 and Alpha
  (Richard Henderson)
- fix sparc64 .plt[32768+] handling
- don't emit .rela.stab on sparc

* Mon Sep 10 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-10
- fix SHF_MERGE on Sparc

* Fri Aug 31 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-9
- on Alpha, copy *r_offset to R_ALPHA_RELATIVE's r_addend

* Thu Aug 30 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-8
- on IA-64, put crtend{,S}.o's .IA_64.unwind section last in
  .IA_64.unwind output section (for compatibility with 7.1 eh)

* Fri Aug 24 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-7
- put RELATIVE relocs first, not last
- enable -z combreloc by default on IA-{32,64}, Alpha, Sparc*

* Thu Aug 23 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-6
- support for -z combreloc
- remove .dynamic patch, -z combreloc patch does this better
- set STT_FUNC default symbol sizes in .endp directive on IA-64

* Mon Jul 16 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-5
- fix last patch (H.J.Lu)

* Fri Jul 13 2001 Jakub Jelinek <jakub@redhat.com> 2.11.90.0.8-4
- fix placing of orphan sections

* Sat Jun 23 2001 Jakub Jelinek <jakub@redhat.com>
- fix SHF_MERGE support on Alpha

* Fri Jun  8 2001 Jakub Jelinek <jakub@redhat.com>
- 2.11.90.0.8
  - some SHF_MERGE suport fixes
- don't build with tooldir /usrusr instead of /usr (#40937)
- reserve few .dynamic entries for prelinking

* Mon Apr 16 2001 Jakub Jelinek <jakub@redhat.com>
- 2.11.90.0.5
  - SHF_MERGE support

* Tue Apr  3 2001 Jakub Jelinek <jakub@redhat.com>
- 2.11.90.0.4
  - fix uleb128 support, so that CVS gcc bootstraps
  - some ia64 fixes

* Mon Mar 19 2001 Jakub Jelinek <jakub@redhat.com>
- add -Bgroup support from Ulrich Drepper

* Fri Mar  9 2001 Jakub Jelinek <jakub@redhat.com>
- hack - add elf_i386_glibc21 emulation

* Fri Feb 16 2001 Jakub Jelinek <jakub@redhat.com>
- 2.10.91.0.2

* Fri Feb  9 2001 Jakub Jelinek <jakub@redhat.com>
- 2.10.1.0.7
- remove ExcludeArch ia64
- back out the -oformat, -omagic and -output change for now

* Fri Dec 15 2000 Jakub Jelinek <jakub@redhat.com>
- Prereq /sbin/install-info

* Tue Nov 21 2000 Jakub Jelinek <jakub@redhat.com>
- 2.10.1.0.2

* Tue Nov 21 2000 Jakub Jelinek <jakub@redhat.com>
- add one more alpha patch

* Wed Nov 15 2000 Jakub Jelinek <jakub@redhat.com>
- fix alpha visibility as problem
- add support for Ultra-III

* Fri Sep 15 2000 Jakub Jelinek <jakub@redhat.com>
- and one more alpha patch

* Fri Sep 15 2000 Jakub Jelinek <jakub@redhat.com>
- two sparc patches

* Mon Jul 24 2000 Jakub Jelinek <jakub@redhat.com>
- 2.10.0.18

* Mon Jul 10 2000 Jakub Jelinek <jakub@redhat.com>
- 2.10.0.12

* Mon Jun 26 2000 Jakub Jelinek <jakub@redhat.com>
- 2.10.0.9

* Thu Jun 15 2000 Jakub Jelinek <jakub@redhat.com>
- fix ld -r

* Mon Jun  5 2000 Jakub Jelinek <jakub@redhat.com>
- 2.9.5.0.46
- use _mandir/_infodir/_lib

* Mon May  8 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.9.5.0.41

* Wed Apr 12 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.9.5.0.34

* Wed Mar 22 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.9.5.0.31

* Fri Feb 04 2000 Cristian Gafton <gafton@redhat.com>
- man pages are compressed
- apply kingdon's patch from #5031

* Wed Jan 19 2000 Jeff Johnson <jbj@redhat.com>
- Permit package to be built with a prefix other than /usr.

* Thu Jan 13 2000 Cristian Gafton <gafton@redhat.com>
- add pacth from hjl to fix the versioning problems in ld

* Tue Jan 11 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Add sparc patches from Jakub Jelinek <jakub@redhat.com>
- Add URL:

* Tue Dec 14 1999 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.9.5.0.22

* Wed Nov 24 1999 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.9.5.0.19

* Sun Oct 24 1999 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.9.5.0.16

* Mon Sep 06 1999 Jakub Jelinek <jj@ultra.linux.cz>
- make shared non-pic libraries work on sparc with glibc 2.1.

* Fri Aug 27 1999 Jim Kingdon
- No source/spec changes, just rebuilding with egcs-1.1.2-18 because
  the older egcs was miscompling gprof.

* Mon Apr 26 1999 Cristian Gafton <gafton@redhat.com>
- back out very *stupid* sparc patch done by HJLu. People, keep out of
  things you don't understand.
- add alpha relax patch from rth

* Mon Apr 05 1999 Cristian Gafton <gafton@redhat.com>
- version  2.9.1.0.23
- patch to make texinfo documentation compile
- auto rebuild in the new build environment (release 2)

* Tue Feb 23 1999 Cristian Gafton <gafton@redhat.com>
- updated to 2.9.1.0.21
- merged with UltraPenguin

* Mon Jan 04 1999 Cristian Gafton <gafton@redhat.com>
- added ARM patch from philb
- version 2.9.1.0.19a
- added a patch to allow arm* arch to be identified as an ARM

* Thu Oct 01 1998 Cristian Gafton <gafton@redhat.com>
- updated to 2.9.1.0.14.

* Sat Sep 19 1998 Jeff Johnson <jbj@redhat.com>
- updated to 2.9.1.0.13.

* Wed Sep 09 1998 Cristian Gafton <gafton@redhat.com>
- updated to 2.9.1.0.12

* Thu Jul  2 1998 Jeff Johnson <jbj@redhat.com>
- updated to 2.9.1.0.7.

* Wed Jun 03 1998 Jeff Johnson <jbj@redhat.com>
- updated to 2.9.1.0.6.

* Tue Jun 02 1998 Erik Troan <ewt@redhat.com>
- added patch from rth to get right offsets for sections in relocateable
  objects on sparc32

* Thu May 07 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Tue May 05 1998 Cristian Gafton <gafton@redhat.com>
- version 2.9.1.0.4 is out; even more, it is public !

* Tue May 05 1998 Jeff Johnson <jbj@redhat.com>
- updated to 2.9.1.0.3.

* Mon Apr 20 1998 Cristian Gafton <gafton@redhat.com>
- updated to 2.9.0.3

* Tue Apr 14 1998 Cristian Gafton <gafton@redhat.com>
- upgraded to 2.9.0.2

* Sun Apr 05 1998 Cristian Gafton <gafton@redhat.com>
- updated to 2.8.1.0.29 (HJ warned me that this thing is a moving target...
  :-)
- "fixed" the damn make install command so that all tools get installed

* Thu Apr 02 1998 Cristian Gafton <gafton@redhat.com>
- upgraded again to 2.8.1.0.28 (at least on alpha now egcs will compile)
- added info packages handling

* Tue Mar 10 1998 Cristian Gafton <gafton@redhat.com>
- upgraded to 2.8.1.0.23

* Mon Mar 02 1998 Cristian Gafton <gafton@redhat.com>
- updated to 2.8.1.0.15 (required to compile the newer glibc)
- all patches are obsoleted now

* Wed Oct 22 1997 Erik Troan <ewt@redhat.com>
- added 2.8.1.0.1 patch from hj
- added patch for alpha palcode form rth
